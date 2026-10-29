// src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { authAPI } from '../api';

const AuthContext = createContext();
export const useAuth = () => useContext(AuthContext);

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000';

const api = axios.create({ baseURL: API_URL });
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const stored = localStorage.getItem('user');
    if (token && stored) {
      try {
        setUser(JSON.parse(stored));
        api.get('/api/ticketing/auth/me')
          .then((res) => {
            const fresh = res.data;
            setUser(fresh);
            localStorage.setItem('user', JSON.stringify(fresh));
          })
          .catch(() => {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            setUser(null);
          });
      } catch {
        setUser(null);
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    try {
      const res = await authAPI.login(email, password);
      const { access_token, user: userData } = res.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      toast.success('Welcome back!');
      return { success: true };
    } catch (err) {
      toast.error(err.response?.data?.error || 'Login failed');
      return { success: false };
    }
  };

  const register = async (data) => {
    try {
      const res = await authAPI.register(data);
      const { access_token, user: userData } = res.data;
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
      toast.success('Account created!');
      return { success: true };
    } catch (err) {
      toast.error(err.response?.data?.error || 'Registration failed');
      return { success: false };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
    toast.success('Logged out');
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, api }}>
      {children}
    </AuthContext.Provider>
  );
};