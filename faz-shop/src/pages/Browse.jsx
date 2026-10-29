// src/pages/Browse.jsx
import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { shopAPI } from '../api';
import { Card, Spinner, EmptyState } from '../components/ui';
import { resolveImageUrl } from '../utils';
import { FaFilter } from 'react-icons/fa';

export default function Browse() {
  const [params, setParams] = useSearchParams();
  const [adverts, setAdverts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);

  const categorySlug = params.get('category') || '';
  const query = params.get('q') || '';
  const premium = params.get('premium') === 'true';

  useEffect(() => {
    shopAPI.listCategories().then((res) => setCategories(res.data || []));
  }, []);

  useEffect(() => {
    setLoading(true);
    shopAPI.listAdverts({
      category: categorySlug || undefined,
      q: query || undefined,
      premium: premium || undefined,
      limit: 60,
    })
      .then((res) => setAdverts(res.data?.items || []))
      .catch(() => setAdverts([]))
      .finally(() => setLoading(false));
  }, [categorySlug, query, premium]);

  const setFilter = (key, value) => {
    const next = new URLSearchParams(params);
    if (value) next.set(key, value);
    else next.delete(key);
    setParams(next);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold gradient-text mb-1">
          {premium ? 'Featured at Matches' : categorySlug ? 'Category' : 'All Products'}
        </h1>
        <p className="text-sm text-gray-500">
          {adverts.length} product{adverts.length !== 1 ? 's' : ''} {query ? `matching "${query}"` : ''}
        </p>
      </div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Filters */}
        <aside className="lg:w-64 flex-shrink-0">
          <Card padding="md">
            <h3 className="font-semibold text-gray-800 mb-3 flex items-center gap-2"><FaFilter /> Filters</h3>
            <div className="space-y-2">
              <button onClick={() => setFilter('category', '')}
                className={`block w-full text-left px-3 py-2 rounded-lg text-sm transition ${!categorySlug ? 'bg-faz-orange text-white' : 'hover:bg-gray-100'}`}>
                All Categories
              </button>
              {categories.map((c) => (
                <button key={c.id} onClick={() => setFilter('category', c.slug)}
                  className={`block w-full text-left px-3 py-2 rounded-lg text-sm transition ${categorySlug === c.slug ? 'bg-faz-orange text-white' : 'hover:bg-gray-100'}`}>
                  {c.icon} {c.name}
                </button>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t">
              <label className="flex items-center gap-2 text-sm cursor-pointer">
                <input type="checkbox" checked={premium} onChange={(e) => setFilter('premium', e.target.checked ? 'true' : '')} />
                Featured only
              </label>
            </div>

            {(categorySlug || premium || query) && (
              <button onClick={() => setParams(new URLSearchParams())}
                className="w-full mt-3 text-xs text-red-600 hover:underline">
                Clear filters
              </button>
            )}
          </Card>
        </aside>

        {/* Results */}
        <div className="flex-1">
          {loading ? (
            <div className="flex justify-center py-20"><Spinner size="xl" /></div>
          ) : adverts.length === 0 ? (
            <EmptyState icon="🔍" title="Nothing found" description="Try adjusting filters or searching for something else." />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
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
                      {a.location_name && <p className="text-xs text-gray-400 mb-2">📍 {a.location_name}</p>}
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
          )}
        </div>
      </div>
    </div>
  );
}