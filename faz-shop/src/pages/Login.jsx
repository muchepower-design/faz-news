// src/pages/Login.jsx
import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Card, Button, Input } from '../components/ui';

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: '', password: '' });
  const [loading, setLoading] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    const { success } = await login(form.email, form.password);
    setLoading(false);
    if (success) navigate('/');
  };

  return (
    <div className="container mx-auto px-4 py-20 max-w-md">
      <Card padding="lg">
        <h1 className="text-2xl font-bold gradient-text mb-1">Welcome back</h1>
        <p className="text-sm text-gray-500 mb-6">Sign in to your FAZ account.</p>

        <form onSubmit={submit} className="space-y-4">
          <Input type="email" label="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input type="password" label="Password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          <Button type="submit" size="lg" loading={loading} className="w-full">Sign In</Button>
        </form>

        <p className="text-sm text-gray-500 mt-4 text-center">
          Don't have an account? <Link to="/register" className="text-faz-orange font-medium hover:underline">Create one</Link>
        </p>
        <p className="text-xs text-gray-400 mt-2 text-center">
          Same account works across FAZ Tickets and the main website.
        </p>
      </Card>
    </div>
  );
}