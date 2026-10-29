// src/pages/MyOrders.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { orderAPI } from '../api';
import { useAuth } from '../context/AuthContext';
import { Card, Button, Badge, Spinner, EmptyState } from '../components/ui';

export default function MyOrders() {
  const { user, loading: authLoading } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (authLoading) return;
    if (!user) { setLoading(false); return; }
    orderAPI.listMyOrders()
      .then((res) => setOrders(res.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user, authLoading]);

  if (authLoading || loading) return <div className="flex justify-center py-32"><Spinner size="xl" /></div>;

  if (!user) {
    return (
      <div className="container mx-auto px-4 py-20 max-w-md">
        <Card padding="lg" className="text-center">
          <h2 className="text-xl font-bold text-gray-800 mb-2">Log in to see your orders</h2>
          <p className="text-sm text-gray-500 mb-4">Or browse products without an account.</p>
          <div className="flex gap-2 justify-center">
            <Link to="/login"><Button>Login</Button></Link>
            <Link to="/browse"><Button variant="outline">Browse</Button></Link>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold gradient-text mb-6">My Orders</h1>

      {orders.length === 0 ? (
        <EmptyState icon="📦" title="No orders yet" description="Your purchases will appear here." action={<Link to="/browse"><Button>Start Shopping</Button></Link>} />
      ) : (
        <div className="space-y-3">
          {orders.map((o) => (
            <Link key={o.id} to={`/order/${o.order_number}`}>
              <Card padding="md" className="hover:shadow-lg transition">
                <div className="flex justify-between items-start flex-wrap gap-2">
                  <div>
                    <p className="font-mono text-xs text-gray-500">{o.order_number.slice(0, 8)}</p>
                    <p className="font-semibold text-gray-800">{o.advert?.title}</p>
                    <p className="text-xs text-gray-500">{new Date(o.created_at).toLocaleDateString()} · {o.currency} {Number(o.total_amount).toFixed(2)}</p>
                  </div>
                  <div className="flex gap-2">
                    <Badge variant={o.payment_status === 'paid' ? 'success' : 'warning'}>{o.payment_status}</Badge>
                    <Badge>{o.fulfillment_status}</Badge>
                  </div>
                </div>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}