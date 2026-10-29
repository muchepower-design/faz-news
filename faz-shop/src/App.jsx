// src/App.jsx
import { Routes, Route } from 'react-router-dom';
import MainLayout from './layouts/MainLayout';
import Home from './pages/Home';
import Browse from './pages/Browse';
import VendorPage from './pages/VendorPage';
import AdvertDetail from './pages/AdvertDetail';
import Checkout from './pages/Checkout';
import PaymentPage from './pages/PaymentPage';
import OrderTracking from './pages/OrderTracking';
import MyOrders from './pages/MyOrders';
import Login from './pages/Login';
import Register from './pages/Register';

export default function App() {
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/browse" element={<Browse />} />
        <Route path="/vendor/:vendorId" element={<VendorPage />} />
        <Route path="/advert/:advertId" element={<AdvertDetail />} />
        <Route path="/checkout/:advertId" element={<Checkout />} />
        <Route path="/pay/:orderNumber" element={<PaymentPage />} />
        <Route path="/order/:orderNumber" element={<OrderTracking />} />
        <Route path="/orders" element={<MyOrders />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
    </MainLayout>
  );
}