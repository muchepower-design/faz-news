// src/pages/Checkout.jsx
import { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { shopAPI, orderAPI } from '../api';
import { useAuth } from '../context/AuthContext';
import { Card, Button, Input, Textarea, Spinner, Badge } from '../components/ui';
import { resolveImageUrl } from '../utils';
import { FaArrowLeft } from 'react-icons/fa';

export default function Checkout() {
  const { advertId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();

  const [advert, setAdvert] = useState(null);
  const [settings, setSettings] = useState({ platform_fee_percent: 0, default_currency: 'ZMW' });
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  const [form, setForm] = useState({
    quantity: 1,
    customer_name: '',
    customer_email: '',
    customer_phone: '',
    delivery_address: '',
    delivery_notes: '',
    payment_method: 'system',
  });

  useEffect(() => {
    Promise.all([shopAPI.getAdvert(advertId), shopAPI.getSettings()])
      .then(([adv, st]) => {
        setAdvert(adv.data);
        setSettings(st.data);

        const pm = adv.data.payment_method;
        const defaultPayment = pm === 'system' ? 'system' : pm === 'offline' ? 'offline' : 'system';

        setForm((f) => ({
          ...f,
          payment_method: defaultPayment,
          customer_name: f.customer_name || user?.full_name || '',
          customer_email: f.customer_email || user?.email || '',
          customer_phone: f.customer_phone || user?.phone || '',
        }));
      })
      .catch(() => toast.error('Failed to load advert'))
      .finally(() => setLoading(false));
  }, [advertId, user]);

  if (loading) return <div className="flex justify-center py-32"><Spinner size="xl" /></div>;
  if (!advert) return <div className="container mx-auto p-8"><Card>Product not found</Card></div>;

  const unit = Number(advert.price || 0);
  const qty = Math.max(1, parseInt(form.quantity) || 1);
  const subtotal = unit * qty;
  const fee = form.payment_method === 'system'
    ? subtotal * (Number(settings.platform_fee_percent || 0) / 100)
    : 0;
  const total = subtotal + fee;
  const currency = advert.currency || settings.default_currency || 'ZMW';

  const canChooseSystem = advert.payment_method === 'system' || advert.payment_method === 'both';
  const canChooseOffline = advert.payment_method === 'offline' || advert.payment_method === 'both';

  const submit = async (e) => {
    e.preventDefault();
    if (!form.customer_name || !form.customer_email || !form.customer_phone || !form.delivery_address) {
      toast.error('Please fill all required fields');
      return;
    }
    setSubmitting(true);
    try {
      const res = await orderAPI.checkout({
        advert_id: advert.id,
        quantity: qty,
        customer_name: form.customer_name,
        customer_email: form.customer_email,
        customer_phone: form.customer_phone,
        delivery_address: form.delivery_address,
        delivery_notes: form.delivery_notes,
        payment_method: form.payment_method,
      });
      const order = res.data;

      if (form.payment_method === 'system') {
        navigate(`/pay/${order.order_number}`);
      } else {
        navigate(`/order/${order.order_number}`);
      }
    } catch (err) {
      toast.error(err.response?.data?.error || 'Checkout failed');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <Link to={`/advert/${advert.id}`} className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-faz-orange mb-4">
        <FaArrowLeft /> Back to product
      </Link>

      <h1 className="text-3xl font-bold gradient-text mb-6">Checkout</h1>

      <div className="grid md:grid-cols-3 gap-6">
        <form onSubmit={submit} className="md:col-span-2 space-y-4">
          <Card padding="lg">
            <h2 className="font-semibold text-gray-800 mb-3">Delivery Details</h2>
            <div className="space-y-3">
              <Input label="Full name" value={form.customer_name} onChange={(e) => setForm({ ...form, customer_name: e.target.value })} required />
              <div className="grid md:grid-cols-2 gap-3">
                <Input type="email" label="Email" value={form.customer_email} onChange={(e) => setForm({ ...form, customer_email: e.target.value })} required />
                <Input label="Phone" value={form.customer_phone} onChange={(e) => setForm({ ...form, customer_phone: e.target.value })} required placeholder="+260..." />
              </div>
              <Textarea label="Delivery address" rows={3} value={form.delivery_address} onChange={(e) => setForm({ ...form, delivery_address: e.target.value })} required />
              <Textarea label="Delivery notes (optional)" rows={2} value={form.delivery_notes} onChange={(e) => setForm({ ...form, delivery_notes: e.target.value })} />
            </div>
          </Card>

          <Card padding="lg">
            <h2 className="font-semibold text-gray-800 mb-3">Payment Method</h2>
            <div className="space-y-2">
              {canChooseSystem && (
                <label className="flex items-start gap-3 p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-faz-orange transition">
                  <input type="radio" name="payment_method" checked={form.payment_method === 'system'} onChange={() => setForm({ ...form, payment_method: 'system' })} className="mt-1" />
                  <div>
                    <p className="font-medium text-gray-800">Pay via FAZ platform</p>
                    <p className="text-xs text-gray-500">Secure mobile money payment. A small platform fee ({settings.platform_fee_percent}%) applies.</p>
                  </div>
                </label>
              )}
              {canChooseOffline && (
                <label className="flex items-start gap-3 p-3 border-2 border-gray-200 rounded-lg cursor-pointer hover:border-faz-orange transition">
                  <input type="radio" name="payment_method" checked={form.payment_method === 'offline'} onChange={() => setForm({ ...form, payment_method: 'offline' })} className="mt-1" />
                  <div>
                    <p className="font-medium text-gray-800">Pay vendor directly</p>
                    <p className="text-xs text-gray-500">Bank or mobile money details will be shown after you place the order.</p>
                  </div>
                </label>
              )}
            </div>
          </Card>

          <Button type="submit" size="lg" loading={submitting} className="w-full">
            Place Order
          </Button>
        </form>

        <aside className="md:col-span-1">
          <Card padding="lg" className="sticky top-24">
            <h2 className="font-semibold text-gray-800 mb-3">Order Summary</h2>
            <div className="flex gap-3 mb-3">
              <div className="w-16 h-16 bg-gray-100 rounded overflow-hidden flex-shrink-0">
                {advert.cover_image && <img src={resolveImageUrl(advert.cover_image)} alt="" className="w-full h-full object-cover" />}
              </div>
              <div className="flex-1">
                <p className="font-medium text-sm text-gray-800 line-clamp-2">{advert.title}</p>
                <p className="text-xs text-gray-500">{currency} {unit.toFixed(2)}</p>
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Quantity</span>
                <div className="flex items-center gap-2">
                  <button type="button" onClick={() => setForm({ ...form, quantity: Math.max(1, qty - 1) })} className="w-6 h-6 border border-gray-300 rounded">-</button>
                  <span className="w-6 text-center">{qty}</span>
                  <button type="button" onClick={() => setForm({ ...form, quantity: qty + 1 })} className="w-6 h-6 border border-gray-300 rounded">+</button>
                </div>
              </div>
              <div className="flex justify-between"><span className="text-gray-600">Subtotal</span><span>{currency} {subtotal.toFixed(2)}</span></div>
              {fee > 0 && <div className="flex justify-between text-xs"><span className="text-gray-500">Platform fee</span><span className="text-gray-500">{currency} {fee.toFixed(2)}</span></div>}
              <div className="flex justify-between pt-2 border-t font-bold text-lg">
                <span>Total</span>
                <span className="text-faz-green">{currency} {total.toFixed(2)}</span>
              </div>
            </div>
          </Card>
        </aside>
      </div>
    </div>
  );
}