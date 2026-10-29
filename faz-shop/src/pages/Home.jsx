// src/pages/Home.jsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { shopAPI } from '../api';
import { Card, Spinner, EmptyState } from '../components/ui';
import { FaArrowRight, FaFire } from 'react-icons/fa';
import { resolveImageUrl } from '../utils'; // small helper below

const HERO_IMG = 'https://images.unsplash.com/photo-1517466787929-bc90951d0974?w=1600&q=80';

export default function Home() {
  const [categories, setCategories] = useState([]);
  const [featured, setFeatured] = useState([]);
  const [recent, setRecent] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      shopAPI.listCategories(),
      shopAPI.listAdverts({ premium: true, limit: 8 }),
      shopAPI.listAdverts({ limit: 8 }),
    ]).then(([cats, feat, rec]) => {
      setCategories(cats.data || []);
      setFeatured(feat.data?.items || []);
      setRecent(rec.data?.items || []);
    }).finally(() => setLoading(false));
  }, []);

  return (
    <>
      {/* HERO */}
      <section className="relative bg-gray-900 text-white overflow-hidden">
        <div className="absolute inset-0 opacity-40">
          <img src={HERO_IMG} alt="" className="w-full h-full object-cover" />
        </div>
        <div className="absolute inset-0 bg-gradient-to-br from-faz-green/80 via-faz-black/60 to-faz-orange/80" />
        <div className="relative container mx-auto px-4 py-24 text-center">
          <h1 className="text-4xl md:text-6xl font-extrabold mb-4 drop-shadow-lg">
            Shop Local. <span className="text-faz-orange">Support Football.</span>
          </h1>
          <p className="text-lg md:text-xl text-white/90 max-w-2xl mx-auto mb-8">
            Discover food, gear, crafts, and services from verified Zambian vendors — for matchday and every day.
          </p>
          <div className="flex flex-wrap gap-3 justify-center">
            <Link to="/browse" className="bg-white text-faz-green font-bold px-8 py-3 rounded-lg hover:bg-faz-orange hover:text-white transition shadow-lg">
              Start Shopping
            </Link>
            <Link to="/browse?premium=true" className="bg-faz-orange text-white font-bold px-8 py-3 rounded-lg hover:bg-red-600 transition shadow-lg flex items-center gap-2">
              <FaFire /> Featured Deals
            </Link>
          </div>
        </div>
      </section>

      {/* CATEGORIES */}
      <section className="container mx-auto px-4 py-12">
        <div className="flex justify-between items-end mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">Shop by Category</h2>
            <p className="text-sm text-gray-500">Everything you need, from the pitch to the stands.</p>
          </div>
        </div>
        {loading ? <Spinner /> : categories.length === 0 ? (
          <EmptyState icon="🏷️" title="No categories yet" description="Categories will appear here once the admin adds them." />
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
            {categories.map((c) => (
              <Link key={c.id} to={`/browse?category=${c.slug}`}>
                <Card className="hover:shadow-lg hover:-translate-y-0.5 transition text-center h-full">
                  <div className="text-4xl mb-2">{c.icon || '🛍️'}</div>
                  <h3 className="font-semibold text-gray-800">{c.name}</h3>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>

      {/* FEATURED */}
      {featured.length > 0 && (
        <section className="bg-orange-50 py-12">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-end mb-6">
              <div>
                <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
                  <FaFire className="text-faz-orange" /> Featured at Matches
                </h2>
                <p className="text-sm text-gray-500">Premium vendor placements attached to specific FAZ matches.</p>
              </div>
              <Link to="/browse?premium=true" className="text-sm text-faz-orange font-medium hover:underline flex items-center gap-1">
                See all <FaArrowRight size={10} />
              </Link>
            </div>
            <AdvertGrid adverts={featured} />
          </div>
        </section>
      )}

      {/* RECENT */}
      <section className="container mx-auto px-4 py-12">
        <div className="flex justify-between items-end mb-6">
          <div>
            <h2 className="text-2xl font-bold text-gray-800">New Arrivals</h2>
            <p className="text-sm text-gray-500">Fresh products from our vendors.</p>
          </div>
          <Link to="/browse" className="text-sm text-faz-orange font-medium hover:underline flex items-center gap-1">
            Browse all <FaArrowRight size={10} />
          </Link>
        </div>
        {loading ? <Spinner /> : recent.length === 0 ? (
          <EmptyState icon="📦" title="No products yet" description="Approved adverts will show up here." />
        ) : (
          <AdvertGrid adverts={recent} />
        )}
      </section>
    </>
  );
}

function AdvertGrid({ adverts }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {adverts.map((a) => (
        <Link key={a.id} to={`/advert/${a.id}`}>
          <div className="group bg-white rounded-xl overflow-hidden border border-gray-200 hover:shadow-xl transition h-full flex flex-col">
            <div className="aspect-[4/3] bg-gray-100 overflow-hidden">
              {a.cover_image ? (
                <img src={resolveImageUrl(a.cover_image)} alt={a.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
              ) : (
                <div className="w-full h-full flex items-center justify-center text-4xl text-gray-300">🛍️</div>
              )}
            </div>
            <div className="p-4 flex-1 flex flex-col">
              <h3 className="font-semibold text-gray-800 line-clamp-2 mb-1">{a.title}</h3>
              {a.vendor?.business_name && (
                <p className="text-xs text-gray-500 mb-2">{a.vendor.business_name}</p>
              )}
              <div className="mt-auto flex justify-between items-center">
                {a.price != null ? (
                  <span className="text-lg font-bold text-faz-green">{a.currency} {Number(a.price).toFixed(2)}</span>
                ) : (
                  <span className="text-sm text-gray-400 italic">Contact for price</span>
                )}
                {a.is_premium && <span className="text-[10px] font-bold bg-faz-orange text-white px-2 py-0.5 rounded-full">PREMIUM</span>}
              </div>
            </div>
          </div>
        </Link>
      ))}
    </div>
  );
}