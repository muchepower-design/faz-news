// src/pages/Register.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, Button, Input } from '../components/ui';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    first_name: '', last_name: '', email: '', phone: '', password: '',
  });
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const { success } = await register({
      ...form,
      full_name: `${form.first_name} ${form.last_name}`.trim(),
      role: 'customer',
    });
    setLoading(false);
    if (success) navigate('/');
  };

  return (
    <div className="container mx-auto px-4 py-20 max-w-md">
      <Card padding="lg">
        <h1 className="text-2xl font-bold gradient-text mb-1">Create an account</h1>
        <p className="text-sm text-gray-500 mb-6">Shop, track orders, and pay securely.</p>

        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <Input label="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} required />
            <Input label="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} required />
          </div>
          <Input type="email" label="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input label="Phone (optional)" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="+260..." />
          <Input type="password" label="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required minLength={6} />
          <Button type="submit" size="lg" loading={loading} className="w-full">Create Account</Button>
        </form>

        <p className="text-sm text-gray-500 mt-4 text-center">
          Already have one? <Link to="/login" className="text-faz-orange font-medium hover:underline">Sign in</Link>
        </p>
      </Card>
    </div>
  );
}