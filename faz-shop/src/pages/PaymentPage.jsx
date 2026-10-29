// src/pages/PaymentPage.jsx
import { useEffect, useRef, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { orderAPI } from '../api';
import { Card, Button, Input, Spinner, Badge } from '../components/ui';

import airtelLogo from './assets/momo/logos/momo_airtel.png'
import mtnLogo from './assets/momo/logos/momo_mtn.png'
import zamtelLogo from './assets/momo/logos/momo_zamtel.jpg'

const providerLogos = {
  'AIRTEL_OAPI_ZMB': airtelLogo,
  'MTN_MOMO_ZMB': mtnLogo,
  'ZAMTEL_ZMB': zamtelLogo,
}

const PROVIDER_NAMES = {
  'AIRTEL_OAPI_ZMB': 'Airtel Money',
  'MTN_MOMO_ZMB': 'MTN Mobile Money',
  'ZAMTEL_ZMB': 'Zamtel Money',
};

export default function PaymentPage() {
  const { orderNumber } = useParams();
  const navigate = useNavigate();
  const pollRef = useRef(null);

  const [order, setOrder] = useState(null);
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [status, setStatus] = useState(null); // 'WAITING' | 'COMPLETED' | 'FAILED'
  const [error, setError] = useState('');

  const [provider, setProvider] = useState('');
  const [phone, setPhone] = useState('');

  useEffect(() => {
    Promise.all([orderAPI.getByNumber(orderNumber), orderAPI.getProviders()])
      .then(([ord, prov]) => {
        setOrder(ord.data);
        setProviders(prov.data || []);
        if (ord.data.payment_status === 'paid') {
          setStatus('COMPLETED');
        }
      })
      .catch(() => { setError('Order not found'); })
      .finally(() => setLoading(false));
    return () => pollRef.current && clearInterval(pollRef.current);
  }, [orderNumber]);

  const isValidPhone = /^0\d{9}$/.test(phone);

  const startPolling = (depositId) => {
    setStatus('WAITING');
    pollRef.current = setInterval(async () => {
      try {
        const res = await orderAPI.checkStatus(depositId);
        if (res.data.status === 'COMPLETED') {
          clearInterval(pollRef.current);
          setStatus('COMPLETED');
          toast.success('Payment successful!');
          setTimeout(() => navigate(`/order/${orderNumber}`), 1500);
        } else if (res.data.success === false) {
          clearInterval(pollRef.current);
          setStatus('FAILED');
          setError(res.data.failureReason?.failureMessage || 'Payment failed');
        }
      } catch {
        clearInterval(pollRef.current);
        setStatus('FAILED');
        setError('Failed to verify payment');
      }
    }, 5000);
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!provider) { toast.error('Select a provider'); return; }
    if (!isValidPhone) { toast.error('Enter a valid 10-digit phone number'); return; }

    setProcessing(true);
    setError('');
    try {
      const res = await orderAPI.initiatePayment({
        target: 'order',
        target_id: orderNumber,
        provider,
        phone_number: '26' + phone,
        amount: String(order.total_amount),
        customer_email: order.customer_email,
      });
      if (res.data.success) {
        toast.success('Payment request sent. Approve on your phone.');
        startPolling(res.data.depositId);
      } else {
        setStatus('FAILED');
        setError(res.data.failureReason?.failureMessage || 'Payment failed');
      }
    } catch (err) {
      setStatus('FAILED');
      setError(err.response?.data?.error || 'Payment failed');
    } finally {
      setProcessing(false);
    }
  };

  if (loading) return <div className="flex justify-center py-32"><Spinner size="xl" /></div>;
  if (!order) return <div className="container mx-auto p-8"><Card>{error || 'Order not found'}</Card></div>;

  return (
    <div className="container mx-auto px-4 py-8 max-w-xl">
      <h1 className="text-3xl font-bold gradient-text mb-6">Complete Payment</h1>

      <Card padding="lg">
        <div className="mb-4 pb-4 border-b">
          <p className="text-xs text-gray-500">Order</p>
          <p className="font-mono text-sm">{order.order_number.slice(0, 8)}</p>
          <p className="text-3xl font-bold text-faz-green mt-2">{order.currency} {Number(order.total_amount).toFixed(2)}</p>
        </div>

        {status === 'WAITING' && (
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-6 text-center">
            <Spinner className="mx-auto mb-3" size="lg" />
            <h3 className="text-lg font-bold text-blue-800">Waiting for approval…</h3>
            <p className="text-sm text-blue-600">Check your phone and enter your Mobile Money PIN.</p>
          </div>
        )}

        {status === 'COMPLETED' && (
          <div className="bg-green-50 border border-green-200 rounded-xl p-6 text-center">
            <span className="text-4xl">✅</span>
            <h3 className="text-lg font-bold text-green-800 mt-2">Payment complete!</h3>
            <p className="text-sm text-green-600">Redirecting to your order…</p>
          </div>
        )}

        {status === 'FAILED' && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-center">
            <span className="text-4xl">❌</span>
            <h3 className="text-lg font-bold text-red-800 mt-2">Payment failed</h3>
            <p className="text-sm text-red-600">{error}</p>
            <Button variant="outline" className="mt-3" onClick={() => { setStatus(null); setError(''); }}>
              Try again
            </Button>
          </div>
        )}

        {!status && (
          <form onSubmit={submit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Mobile Money Provider</label>
              <div className="grid grid-cols-3 gap-2">
                {providers.map((p) => (
                  <button key={p.provider} type="button" disabled={!p.deposit_operational}
                    onClick={() => setProvider(p.provider)}
                    className={`p-3 border-2 rounded-lg text-center transition ${
                      !p.deposit_operational ? 'opacity-40 cursor-not-allowed border-gray-200' :
                      provider === p.provider ? 'border-faz-orange bg-orange-50' : 'border-gray-200 hover:border-gray-300'
                    }`}>
                    <img
                          src={providerLogos[p.provider] || '📱'}
                          alt={PROVIDER_NAMES[p.provider] || p.provider}
                          className="w-30 h-10 object-contain"
                        />
                    <p className="text-xs font-medium">{PROVIDER_NAMES[p.provider] || p.provider}</p>
                  </button>
                ))}
              </div>
            </div>

            <Input label="Mobile Money Phone Number" value={phone} onChange={(e) => setPhone(e.target.value.replace(/\D/g, '').slice(0, 10))} placeholder="0xxxxxxxxx" inputMode="numeric" required />

            <Button type="submit" size="lg" loading={processing} disabled={!isValidPhone || !provider} className="w-full">
              Pay {order.currency} {Number(order.total_amount).toFixed(2)}
            </Button>
          </form>
        )}
      </Card>
    </div>
  );
}