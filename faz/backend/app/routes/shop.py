from flask import Blueprint, request, jsonify, abort, make_response
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.database import db
from app.models import ProductCategory, Product, Cart, CartItem, Order, OrderItem
from app.schemas import ProductCategoryCreate, ProductCreate, AddToCart, CheckoutData, PaymentInitiate
from app.auth import get_current_user, get_current_user_optional, admin_required
import uuid, os, requests, re
from datetime import datetime

bp = Blueprint('shop', __name__)

PAWAPAY_API_KEY = os.environ.get('PAWAPAY_API_KEY')
PAWAPAY_BASE_URL = "https://api.pawapay.io/v2"

def get_pawapay_headers():
    return {
        "Authorization": f"Bearer {PAWAPAY_API_KEY}",
        "Content-Type": "application/json"
    }

# ============ CATEGORIES ============
@bp.route('/categories', methods=['GET'])
def get_categories():
    categories = ProductCategory.query.filter_by(is_active=True).order_by(ProductCategory.display_order).all()
    return jsonify([c.to_dict() for c in categories])

@bp.route('/categories', methods=['POST'])
@jwt_required()
@admin_required
def create_category():
    data = request.get_json()
    category = ProductCategory(**data)
    db.session.add(category)
    db.session.commit()
    return jsonify({"id": str(category.id)}), 201

@bp.route('/categories/<category_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_category(category_id):
    category = ProductCategory.query.get(category_id)
    if not category:
        abort(404)
    data = request.get_json()
    for key, value in data.items():
        setattr(category, key, value)
    db.session.commit()
    return jsonify({"message": "Updated"})

@bp.route('/categories/<category_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_category(category_id):
    category = ProductCategory.query.get(category_id)
    if not category:
        abort(404)
    category.is_active = False
    db.session.commit()
    return jsonify({"message": "Deleted"})

# ============ PRODUCTS ============
@bp.route('/products', methods=['GET'])
def get_products():
    category_id = request.args.get('category_id')
    featured = request.args.get('featured') == 'true'
    skip = int(request.args.get('skip', 0))
    limit = int(request.args.get('limit', 20))
    query = Product.query.filter_by(is_active=True)
    if category_id:
        query = query.filter_by(category_id=category_id)
    if featured:
        query = query.filter_by(is_featured=True)
    products = query.order_by(Product.created_at.desc()).offset(skip).limit(limit).all()
    return jsonify([p.to_dict() for p in products])

@bp.route('/products/<product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        abort(404)
    return jsonify(product.to_dict())

@bp.route('/products', methods=['POST'])
@jwt_required()
@admin_required
def create_product():
    data = request.get_json()
    slug = data['name'].lower().replace(" ", "-")
    product = Product(slug=slug, **data)
    db.session.add(product)
    db.session.commit()
    return jsonify({"id": str(product.id)}), 201

@bp.route('/products/<product_id>', methods=['PUT'])
@jwt_required()
@admin_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        abort(404)
    data = request.get_json()
    for key, value in data.items():
        setattr(product, key, value)
    db.session.commit()
    return jsonify({"message": "Updated"})

@bp.route('/products/<product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        abort(404)
    product.is_active = False
    db.session.commit()
    return jsonify({"message": "Deleted"})

# ============ CART ============
@bp.route('/cart', methods=['GET'])
def get_cart():
    session_id = request.cookies.get('cart_session_id')
    auth_header = request.headers.get('Authorization')
    user = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        # try to get user
        try:
            verify_jwt_in_request()
            user = get_current_user()  # but we need optional
        except:
            pass
    # For optional user, we can use a helper
    if user:
        cart = Cart.query.filter_by(user_id=user.id).first()
    else:
        cart = Cart.query.filter_by(session_id=session_id).first() if session_id else None
    if not cart:
        return jsonify({"items": [], "subtotal": 0, "total": 0})
    items = []
    subtotal = 0
    for item in cart.items:
        product = item.product
        if product:
            item_data = {
                "id": str(item.id),
                "product_id": str(product.id),
                "product_name": product.name,
                "product_image": product.image_url,
                "quantity": item.quantity,
                "size": item.size,
                "color": item.color,
                "unit_price": item.price_at_add,
                "subtotal": item.quantity * item.price_at_add
            }
            items.append(item_data)
            subtotal += item.quantity * item.price_at_add
    return jsonify({"items": items, "subtotal": subtotal, "total": subtotal})

@bp.route('/cart/add', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    # get session_id
    session_id = request.cookies.get('cart_session_id')
    if not session_id:
        session_id = str(uuid.uuid4())
    # check user
    auth_header = request.headers.get('Authorization')
    user = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            verify_jwt_in_request()
            user = get_current_user()
        except:
            pass
    # get or create cart
    cart = None
    if user:
        cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart and session_id:
        cart = Cart.query.filter_by(session_id=session_id).first()
    if not cart:
        cart = Cart(
            user_id=user.id if user else None,
            session_id=session_id
        )
        db.session.add(cart)
        db.session.commit()
    # get product
    product = Product.query.get(data['product_id'])
    if not product:
        abort(404, "Product not found")
    if product.stock_quantity < data.get('quantity', 1):
        abort(400, "Insufficient stock")
    # check existing item
    existing_item = CartItem.query.filter_by(cart_id=cart.id, product_id=product.id, size=data.get('size'), color=data.get('color')).first()
    if existing_item:
        existing_item.quantity += data.get('quantity', 1)
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            quantity=data.get('quantity', 1),
            size=data.get('size'),
            color=data.get('color'),
            price_at_add=product.price
        )
        db.session.add(item)
    db.session.commit()
    response = jsonify({"message": "Item added to cart", "session_id": session_id})
    response.set_cookie('cart_session_id', session_id, max_age=2592000, path='/', httponly=True, samesite='Lax')
    return response

@bp.route('/cart/update/<item_id>', methods=['PUT'])
def update_cart_item(item_id):
    data = request.get_json()
    quantity = data.get('quantity')
    item = CartItem.query.get(item_id)
    if not item:
        abort(404)
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return jsonify({"message": "Cart updated"})

@bp.route('/cart/remove/<item_id>', methods=['DELETE'])
def remove_cart_item(item_id):
    item = CartItem.query.get(item_id)
    if not item:
        abort(404)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed"})

# ============ CHECKOUT ============
@bp.route('/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    session_id = request.cookies.get('cart_session_id')
    auth_header = request.headers.get('Authorization')
    user = None
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        try:
            verify_jwt_in_request()
            user = get_current_user()
        except:
            pass
    cart = None
    if user:
        cart = Cart.query.filter_by(user_id=user.id).first()
    if not cart and session_id:
        cart = Cart.query.filter_by(session_id=session_id).first()
    if not cart or not cart.items:
        abort(400, "Cart is empty")
    # validate required fields
    required = ['customer_name', 'customer_email', 'customer_phone', 'shipping_address']
    for field in required:
        if not data.get(field):
            abort(400, f"{field} is required")
    subtotal = sum(item.quantity * item.price_at_add for item in cart.items)
    order_number = f"FAZ{datetime.now().strftime('%Y%m%d')}{str(uuid.uuid4())[:8].upper()}"
    order = Order(
        order_number=order_number,
        user_id=user.id if user else None,
        customer_name=data['customer_name'],
        customer_email=data['customer_email'],
        customer_phone=data['customer_phone'],
        shipping_address=data['shipping_address'],
        subtotal=subtotal,
        delivery_fee=0,
        total_amount=subtotal,
        payment_status='pending',
        order_status='pending'
    )
    db.session.add(order)
    db.session.flush()
    for cart_item in cart.items:
        product = cart_item.product
        if product:
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                product_name=product.name,
                product_image=product.image_url,
                quantity=cart_item.quantity,
                size=cart_item.size,
                color=cart_item.color,
                unit_price=cart_item.price_at_add,
                subtotal=cart_item.quantity * cart_item.price_at_add
            )
            db.session.add(order_item)
    # clear cart
    for item in cart.items:
        db.session.delete(item)
    db.session.delete(cart)
    db.session.commit()
    return jsonify({"order_id": str(order.id), "order_number": order_number, "total_amount": order.total_amount})

# ============ PAYMENT ============
@bp.route('/payment/initiate', methods=['POST'])
def initiate_payment():
    data = request.get_json()
    order_id = data.get('order_id')
    provider = data.get('provider')
    phone_number = data.get('phone_number')
    if not all([order_id, provider, phone_number]):
        abort(400, "Missing required fields")
    order = Order.query.get(order_id)
    if not order:
        abort(404, "Order not found")
    if order.payment_status != 'pending':
        abort(400, f"Order already processed. Status: {order.payment_status}")
    # format phone
    raw_phone = phone_number
    clean_digits = re.sub(r'\D', '', raw_phone)
    if clean_digits.startswith('0'):
        clean_digits = clean_digits[1:]
    if clean_digits.startswith('260'):
        clean_digits = clean_digits[3:]
    if clean_digits.startswith('26'):
        clean_digits = clean_digits[2:]
    if len(clean_digits) != 9:
        abort(400, "Invalid phone number. Expected 9 digits after cleaning.")
    formatted_phone = f"260{clean_digits}"
    deposit_id = str(uuid.uuid4())
    client_ref = f"FAZ{order.order_number[:20]}".replace('-', '').replace('_', '')
    payload = {
        "depositId": deposit_id,
        "payer": {
            "type": "MMO",
            "accountDetails": {
                "phoneNumber": formatted_phone,
                "provider": provider
            }
        },
        "amount": str(order.total_amount),
        "currency": "ZMW",
        "clientReferenceId": client_ref,
        "customerMessage": "FAZ Payment",
        "metadata": [
            {"orderId": str(order.id)},
            {"customerId": order.customer_email, "isPII": True}
        ]
    }
    try:
        resp = requests.post(f"{PAWAPAY_BASE_URL}/deposits", json=payload, headers=get_pawapay_headers(), timeout=30)
        pawa_resp = resp.json()
        if resp.status_code == 200:
            status = pawa_resp.get('status')
            if status in ['ACCEPTED', 'DUPLICATE_IGNORED']:
                order.payment_reference = pawa_resp.get('depositId', deposit_id)
                order.payment_method = provider
                db.session.commit()
                return jsonify({'success': True, 'depositId': order.payment_reference, 'message': 'Payment request sent.'})
            else:
                order.payment_status = 'failed'
                db.session.commit()
                return jsonify({'success': False, 'status': status, 'failureReason': pawa_resp.get('failureReason')})
        else:
            order.payment_status = 'failed'
            db.session.commit()
            return jsonify({'success': False, 'status': 'ERROR'})
    except Exception as e:
        abort(503, f"Payment service unavailable: {str(e)}")

@bp.route('/payment/status/<deposit_id>', methods=['GET'])
def check_payment_status(deposit_id):
    order = Order.query.filter_by(payment_reference=deposit_id).first()
    if not order:
        abort(404, "Deposit not found")
    try:
        resp = requests.get(f"{PAWAPAY_BASE_URL}/deposits/{deposit_id}", headers=get_pawapay_headers(), timeout=10)
        data = resp.json()
        if resp.status_code == 200 and data.get('status') == 'FOUND':
            deposit_data = data.get('data')
            deposit_status = deposit_data.get('status')
            if deposit_status == 'COMPLETED':
                for item in order.items:
                    product = Product.query.get(item.product_id)
                    if product:
                        product.stock_quantity -= item.quantity
                order.payment_status = 'paid'
                order.order_status = 'processing'
                db.session.commit()
                return jsonify({'success': True, 'status': 'COMPLETED'})
            elif deposit_status == 'FAILED':
                order.payment_status = 'failed'
                db.session.commit()
                return jsonify({'success': False, 'status': 'FAILED', 'failureReason': deposit_data.get('failureReason')})
            else:
                return jsonify({'success': True, 'status': deposit_status})
        else:
            order.payment_status = 'failed'
            db.session.commit()
            return jsonify({'success': False, 'status': 'ERROR'})
    except:
        abort(503, "Payment service unavailable")

@bp.route('/payment/providers', methods=['GET'])
def get_payment_providers():
    try:
        resp = requests.get(f"{PAWAPAY_BASE_URL}/availability", headers=get_pawapay_headers(), timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            providers = []
            for country in data:
                if country.get('country') == 'ZMB':
                    for prov in country.get('providers', []):
                        deposit_status = prov.get('operationTypes', {}).get('DEPOSIT', 'CLOSED')
                        providers.append({
                            'provider': prov['provider'],
                            'name': prov['provider'].replace('_ZMB', '').replace('_OAPI_ZMB', '').replace('MOMO', ' Mobile Money'),
                            'country': 'ZMB',
                            'deposit_operational': deposit_status == 'OPERATIONAL'
                        })
            return jsonify(providers)
        else:
            return jsonify([])
    except:
        return jsonify([])

@bp.route('/orders/<order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        abort(404)
    return jsonify(order.to_dict())