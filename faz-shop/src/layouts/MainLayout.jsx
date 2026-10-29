// src/layouts/MainLayout.jsx
import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FaShoppingBag, FaUserCircle, FaSignOutAlt, FaSearch, FaBars, FaTimes, FaFacebookF, FaYoutube, FaInstagram, FaEnvelope, FaPhone } from 'react-icons/fa';
import { FaXTwitter } from 'react-icons/fa6';
import logoImage from '../pages/assets/logo/faz logo.jpg'; // adjust if needed

const MAIN = import.meta.env.VITE_API_FRONTEND_MAIN || '#';
const TICKETS = import.meta.env.VITE_API_FRONTEND_TICKETS || '#';

export default function MainLayout({ children }) {
  const { user, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  const submitSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/browse?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchQuery('');
      setMobileOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Top bar */}
      <div className="bg-faz-black text-white text-xs">
        <div className="container mx-auto px-4 py-2 flex justify-between items-center">
          <div className="flex items-center gap-3">
            <a href="https://web.facebook.com/FootballAssociationZambia" target="_blank" rel="noopener noreferrer" className="hover:text-faz-orange"><FaFacebookF /></a>
            <a href="https://x.com/FAZFootball" target="_blank" rel="noopener noreferrer" className="hover:text-faz-orange"><FaXTwitter /></a>
            <a href="https://www.youtube.com/@FAZTVOfficial" target="_blank" rel="noopener noreferrer" className="hover:text-faz-orange"><FaYoutube /></a>
            <a href="https://instagram.com" target="_blank" rel="noopener noreferrer" className="hover:text-faz-orange"><FaInstagram /></a>
          </div>
          <div className="hidden md:flex items-center gap-4">
            <a href="tel:+260211123456" className="hover:text-faz-orange flex items-center gap-1"><FaPhone size={10} /> +260 211 123456</a>
            <a href="mailto:shop@faz.zm" className="hover:text-faz-orange flex items-center gap-1"><FaEnvelope size={10} /> shop@faz.zm</a>
          </div>
        </div>
      </div>

      {/* Main nav */}
      <header className="bg-white shadow-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-3 flex items-center justify-between gap-4">
          <Link to="/" className="flex items-center gap-2 flex-shrink-0">
            <div className="w-10 h-10 bg-gradient-to-br from-faz-green to-faz-orange rounded-full overflow-hidden flex items-center justify-center">
              <img src={logoImage} alt="FAZ" className="w-full h-full object-contain" onError={(e) => { e.currentTarget.style.display = 'none' }} />
            </div>
            <div>
              <h1 className="text-lg font-bold gradient-text leading-tight">FAZ Shop</h1>
              <p className="text-[10px] text-gray-500 -mt-0.5">Football Association of Zambia</p>
            </div>
          </Link>

          <form onSubmit={submitSearch} className="hidden md:flex flex-1 max-w-xl">
            <div className="relative w-full">
              <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search products, vendors, services…"
                className="w-full pl-10 pr-4 py-2 bg-gray-100 border border-transparent focus:bg-white focus:border-faz-orange rounded-lg text-sm outline-none transition"
              />
            </div>
          </form>

          <div className="flex items-center gap-2">
            <Link to="/browse" className="hidden lg:block text-sm text-gray-700 hover:text-faz-orange font-medium px-3 py-2">Browse</Link>
            <a href={TICKETS} target="_blank" rel="noopener noreferrer" className="hidden lg:block text-sm text-gray-700 hover:text-faz-orange font-medium px-3 py-2">Tickets</a>
            <a href={MAIN} target="_blank" rel="noopener noreferrer" className="hidden lg:block text-sm text-gray-700 hover:text-faz-orange font-medium px-3 py-2">FAZ Home</a>

            {user ? (
              <div className="flex items-center gap-2">
                <Link to="/orders" className="text-sm text-gray-700 hover:text-faz-orange px-3 py-2">My Orders</Link>
                <div className="relative group">
                  <button className="w-9 h-9 rounded-full bg-gradient-to-br from-faz-green to-faz-orange text-white flex items-center justify-center font-bold">
                    {(user.first_name?.[0] || user.email?.[0] || 'U').toUpperCase()}
                  </button>
                  <div className="absolute right-0 mt-2 w-40 bg-white border border-gray-200 rounded-lg shadow-lg opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                    <button onClick={logout} className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg">
                      <FaSignOutAlt className="inline mr-2" /> Sign Out
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="hidden md:flex items-center gap-2">
                <Link to="/login" className="text-sm text-gray-700 hover:text-faz-orange px-3 py-2">Login</Link>
                <Link to="/register" className="text-sm font-medium text-white bg-gradient-to-r from-faz-orange to-faz-red px-4 py-2 rounded-lg hover:opacity-90 transition">Sign Up</Link>
              </div>
            )}

            <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden p-2 text-gray-700">
              {mobileOpen ? <FaTimes /> : <FaBars />}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white px-4 py-3 space-y-2">
            <form onSubmit={submitSearch} className="mb-2">
              <div className="relative">
                <FaSearch className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 text-sm" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Search…"
                  className="w-full pl-10 pr-4 py-2 bg-gray-100 rounded-lg text-sm outline-none"
                />
              </div>
            </form>
            <Link to="/browse" onClick={() => setMobileOpen(false)} className="block py-2 text-sm">Browse</Link>
            <a href={TICKETS} target="_blank" rel="noopener noreferrer" className="block py-2 text-sm">Tickets</a>
            <a href={MAIN} target="_blank" rel="noopener noreferrer" className="block py-2 text-sm">FAZ Home</a>
            {!user && (
              <>
                <Link to="/login" onClick={() => setMobileOpen(false)} className="block py-2 text-sm">Login</Link>
                <Link to="/register" onClick={() => setMobileOpen(false)} className="block py-2 text-sm">Register</Link>
              </>
            )}
            {user && (
              <Link to="/orders" onClick={() => setMobileOpen(false)} className="block py-2 text-sm">My Orders</Link>
            )}
          </div>
        )}
      </header>

      <main className="flex-1">{children}</main>

      <footer className="bg-gray-900 text-white mt-16">
        <div className="container mx-auto px-4 py-10 grid md:grid-cols-4 gap-8">
          <div>
            <h3 className="font-bold text-lg gradient-text mb-2">FAZ Shop</h3>
            <p className="text-sm text-gray-400">The official e-commerce platform of the Football Association of Zambia.</p>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Shop</h4>
            <ul className="space-y-1 text-sm text-gray-400">
              <li><Link to="/browse" className="hover:text-faz-orange">Browse All</Link></li>
              <li><Link to="/browse?premium=true" className="hover:text-faz-orange">Featured</Link></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">FAZ</h4>
            <ul className="space-y-1 text-sm text-gray-400">
              <li><a href={MAIN} className="hover:text-faz-orange">Main Website</a></li>
              <li><a href={TICKETS} className="hover:text-faz-orange">Buy Tickets</a></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold mb-3">Contact</h4>
            <ul className="space-y-1 text-sm text-gray-400">
              <li>Football House, Lusaka</li>
              <li>shop@faz.zm</li>
              <li>+260 211 123 456</li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 py-4 text-center text-xs text-gray-500">
          © {new Date().getFullYear()} Football Association of Zambia. All rights reserved.
        </div>
      </footer>
    </div>
  );
}