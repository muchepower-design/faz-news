// src/pages/OrderTracking.jsx
import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import toast from 'react-hot-toast';
import { orderAPI } from '../api';
import { Card, Button, Badge, Spinner, EmptyState } from '../components/ui';
import { useAuth } from '../context/AuthContext';
import { resolveImageUrl } from '../utils';
import { FaCheckCircle, FaTruck, FaBox, FaClipboardCheck } from 'react-icons/fa';

export default function OrderTracking() {
  const { orderNumber } = useParams();
  const { user } = useAuth();
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [confirming, setConfirming] = useState(false);

  const load = () => {
    setLoading(true);
    orderAPI.getByNumber(orderNumber)
      .then((res) => setOrder(res.data))
      .catch(() => toast.error('Failed to load order'))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(); }, [orderNumber]);

  const confirmReceipt = async () => {
    if (!user) {
      toast.error('Please log in to confirm receipt');
      return;
    }
    if (!confirm('Have you received your order and are you satisfied?')) return;
    setConfirming(true);
    try {
      const res = await orderAPI.confirmReceipt(orderNumber);
      setOrder(res.data);
      toast.success('Thanks! Order completed.');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to confirm');
    } finally { setConfirming(false); }
  };

  if (loading) return <div className="flex justify-center py-32"><Spinner size="xl" /></div>;
  if (!order) return <div className="container mx-auto p-8"><EmptyState icon="📦" title="Order not found" /></div>;

  const isPaid = order.payment_status === 'paid';
  const isOffline = order.payment_method === 'offline';
  const isComplete = !!order.customer_confirmed_at;
  const isDelivered = order.fulfillment_status === 'delivered' || order.fulfillment_status === 'completed';

  const advert = order.advert;

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <p className="text-xs text-gray-500">ORDER</p>
        <h1 className="text-2xl font-bold text-gray-800 font-mono">{order.order_number}</h1>
        <div className="flex flex-wrap gap-2 mt-2">
          <Badge variant={isPaid ? 'success' : 'warning'}>Payment: {order.payment_status}</Badge>
          <Badge variant={isComplete ? 'success' : 'default'}>Fulfillment: {order.fulfillment_status}</Badge>
          {order.payment_method === 'offline' && <Badge variant="orange">Direct-to-vendor</Badge>}
        </div>
      </div>

      {/* OFF-LINE payment banner */}
      {isOffline && !isComplete && (
        <Card padding="lg" className="mb-6 border-l-4 border-faz-orange">
          <h3 className="font-bold text-gray-800 mb-2">Pay the vendor directly</h3>
          <p className="text-sm text-gray-600 mb-3">
            Your order is placed. Please pay the vendor to begin fulfillment.
            Reference <strong>{order.order_number.slice(0, 8)}</strong> when paying.
          </p>
          {advert?.vendor && (
            <div className="text-sm bg-gray-50 p-3 rounded space-y-1">
              <p className="font-medium">{advert.vendor.business_name}</p>
              {advert.vendor.bank_name && <p><span className="text-gray-500">Bank:</span> {advert.vendor.bank_name}</p>}
              {advert.vendor.bank_account_name && <p><span className="text-gray-500">A/C name:</span> {advert.vendor.bank_account_name}</p>}
              {advert.vendor.bank_account_number && <p><span className="text-gray-500">A/C number:</span> {advert.vendor.bank_account_number}</p>}
              {advert.vendor.mobile_money_provider && <p><span className="text-gray-500">Mobile:</span> {advert.vendor.mobile_money_provider} — {advert.vendor.mobile_money_number}</p>}
              {advert.vendor.contact_phone && <p><span className="text-gray-500">Phone:</span> {advert.vendor.contact_phone}</p>}
              {advert.vendor.offline_instructions && <p className="mt-2 text-gray-700 whitespace-pre-wrap">{advert.vendor.offline_instructions}</p>}
            </div>
          )}
        </Card>
      )}

      <div className="grid md:grid-cols-3 gap-6">
        <div className="md:col-span-2 space-y-6">
          {/* Timeline */}
          <Card padding="lg">
            <h2 className="font-bold text-gray-800 mb-4">Tracking Timeline</h2>
            <div className="space-y-4">
              {(order.timeline || []).map((t) => (
                <div key={t.id} className="flex gap-3">
                  <div className="flex flex-col items-center">
                    <div className="w-3 h-3 rounded-full bg-faz-orange" />
                    <div className="w-px flex-1 bg-gray-200 my-1" />
                  </div>
                  <div className="flex-1 pb-4">
                    <p className="font-medium text-gray-800 capitalize">{t.status.replace(/_/g, ' ')}</p>
                    {t.note && <p className="text-sm text-gray-600">{t.note}</p>}
                    <p className="text-xs text-gray-400 mt-0.5">
                      {new Date(t.created_at).toLocaleString()}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            {isDelivered && !isComplete && (
              <div className="mt-4 pt-4 border-t">
                <Button onClick={confirmReceipt} loading={confirming} className="w-full" size="lg">
                  <FaCheckCircle /> Confirm Receipt
                </Button>
                <p className="text-xs text-gray-500 mt-2 text-center">
                  Confirm only after you've received the item.
                </p>
              </div>
            )}

            {isComplete && (
              <div className="mt-4 pt-4 border-t bg-green-50 rounded-lg p-4 text-center">
                <FaCheckCircle className="text-green-600 text-3xl mx-auto mb-2" />
                <p className="font-semibold text-green-800">Order completed</p>
                <p className="text-xs text-green-700">Thanks for shopping with FAZ!</p>
              </div>
            )}
          </Card>

          {/* Delivery */}
          <Card padding="lg">
            <h2 className="font-bold text-gray-800 mb-3">Delivery</h2>
            <p className="text-sm"><span className="text-gray-500">Name:</span> {order.customer_name}</p>
            <p className="text-sm"><span className="text-gray-500">Phone:</span> {order.customer_phone}</p>
            <p className="text-sm"><span className="text-gray-500">Address:</span> {order.delivery_address}</p>
            {order.delivery_notes && <p className="text-sm"><span className="text-gray-500">Notes:</span> {order.delivery_notes}</p>}
            {order.courier_name && <p className="text-sm mt-2"><FaTruck className="inline mr-1 text-faz-orange" /> {order.courier_name} {order.tracking_number && `— ${order.tracking_number}`}</p>}
          </Card>
        </div>

        <aside>
          <Card padding="lg">
            <h2 className="font-bold text-gray-800 mb-3">Order Summary</h2>
            {advert && (
              <div className="flex gap-3 mb-3 pb-3 border-b">
                <div className="w-14 h-14 bg-gray-100 rounded overflow-hidden flex-shrink-0">
                  {advert.cover_image && <img src={resolveImageUrl(advert.cover_image)} alt="" className="w-full h-full object-cover" />}
                </div>
                <div className="flex-1 min-w-0">
                  <Link to={`/advert/${advert.id}`} className="text-sm font-medium hover:text-faz-orange line-clamp-2">{advert.title}</Link>
                  <p className="text-xs text-gray-500">×{order.quantity}</p>
                </div>
              </div>
            )}
            <div className="space-y-1 text-sm">
              <div className="flex justify-between"><span className="text-gray-600">Subtotal</span><span>{order.currency} {Number(order.subtotal).toFixed(2)}</span></div>
              {Number(order.admin_fee) > 0 && <div className="flex justify-between text-xs"><span className="text-gray-500">Platform fee</span><span className="text-gray-500">{order.currency} {Number(order.admin_fee).toFixed(2)}</span></div>}
              <div className="flex justify-between pt-2 border-t font-bold"><span>Total</span><span className="text-faz-green">{order.currency} {Number(order.total_amount).toFixed(2)}</span></div>
            </div>
          </Card>
        </aside>
      </div>
    </div>
  );
}