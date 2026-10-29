// src/pages/VendorPage.jsx
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { shopAPI } from '../api';
import { Card, Button, Badge, Spinner, EmptyState } from '../components/ui';
import { resolveImageUrl } from '../utils';
import {
  FaMapMarkerAlt, FaPhone, FaEnvelope, FaWhatsapp,
  FaGlobe, FaArrowLeft, FaStore,
} from 'react-icons/fa';

export default function VendorPage() {
  const { vendorId } = useParams();
  const [vendor, setVendor] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    shopAPI.getVendor(vendorId)
      .then((res) => setVendor(res.data))
      .catch(() => setVendor(null))
      .finally(() => setLoading(false));
  }, [vendorId]);

  if (loading) {
    return (
      <div className="flex justify-center py-32">
        <Spinner size="xl" />
      </div>
    );
  }

  if (!vendor) {
    return (
      <div className="container mx-auto px-4 py-20">
        <EmptyState
          icon="🏪"
          title="Vendor not found"
          description="This vendor may not exist or is not currently active."
          action={
            <Link to="/browse">
              <Button>Browse all products</Button>
            </Link>
          }
        />
      </div>
    );
  }

  const adverts = vendor.adverts || [];
  const hasCoords =
    vendor.latitude != null && vendor.longitude != null;
  const mapsUrl = hasCoords
    ? `https://www.google.com/maps/search/?api=1&query=${vendor.latitude},${vendor.longitude}`
    : vendor.location_name
      ? `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(vendor.location_name)}`
      : null;

  return (
    <div className="container mx-auto px-4 py-8">
      <Link
        to="/browse"
        className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-faz-orange mb-4"
      >
        <FaArrowLeft /> Back to browse
      </Link>

      {/* Banner */}
      <div className="relative rounded-2xl overflow-hidden mb-6 bg-gradient-to-br from-faz-green via-faz-orange to-faz-red">
        {vendor.banner_url && (
          <img
            src={resolveImageUrl(vendor.banner_url)}
            alt={vendor.business_name}
            className="absolute inset-0 w-full h-full object-cover opacity-60"
          />
        )}
        <div className="relative px-6 py-12 md:py-16 text-white">
          <div className="flex flex-col md:flex-row md:items-end gap-4">
            <div className="w-24 h-24 rounded-2xl bg-white shadow-xl overflow-hidden flex items-center justify-center flex-shrink-0 border-4 border-white">
              {vendor.logo_url ? (
                <img
                  src={resolveImageUrl(vendor.logo_url)}
                  alt={vendor.business_name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <FaStore className="text-faz-orange text-4xl" />
              )}
            </div>
            <div className="flex-1 min-w-0">
              <Badge variant="success" className="mb-2">
                Verified FAZ Vendor
              </Badge>
              <h1 className="text-3xl md:text-4xl font-bold drop-shadow-lg">
                {vendor.business_name}
              </h1>
              {vendor.location_name && (
                <p className="text-sm text-white/90 mt-1 flex items-center gap-1">
                  <FaMapMarkerAlt /> {vendor.location_name}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Left: about + contact */}
        <aside className="lg:col-span-1 space-y-4">
          <Card padding="lg">
            <h2 className="font-bold text-gray-800 mb-3">About</h2>
            {vendor.description ? (
              <p className="text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                {vendor.description}
              </p>
            ) : (
              <p className="text-sm text-gray-400 italic">
                No description provided.
              </p>
            )}

            <div className="mt-4 pt-4 border-t space-y-2 text-sm">
              {vendor.contact_phone && (
                <a
                  href={`tel:${vendor.contact_phone}`}
                  className="flex items-center gap-2 text-gray-700 hover:text-faz-orange transition"
                >
                  <FaPhone className="text-faz-orange" />
                  {vendor.contact_phone}
                </a>
              )}
              {vendor.contact_email && (
                <a
                  href={`mailto:${vendor.contact_email}`}
                  className="flex items-center gap-2 text-gray-700 hover:text-faz-orange transition"
                >
                  <FaEnvelope className="text-faz-orange" />
                  {vendor.contact_email}
                </a>
              )}
              {vendor.contact_whatsapp && (
                <a
                  href={`https://wa.me/${vendor.contact_whatsapp.replace(/\D/g, '')}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-gray-700 hover:text-green-600 transition"
                >
                  <FaWhatsapp className="text-green-600" />
                  WhatsApp
                </a>
              )}
              {vendor.website_url && (
                <a
                  href={vendor.website_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-gray-700 hover:text-faz-orange transition"
                >
                  <FaGlobe className="text-faz-orange" />
                  Visit website
                </a>
              )}
              {mapsUrl && (
                <a
                  href={mapsUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 text-gray-700 hover:text-faz-orange transition"
                >
                  <FaMapMarkerAlt className="text-faz-orange" />
                  {vendor.location_name || 'View on map'}
                </a>
              )}
            </div>
          </Card>

          <Card padding="md" className="text-center">
            <p className="text-3xl font-bold gradient-text">{adverts.length}</p>
            <p className="text-sm text-gray-500">
              {adverts.length === 1 ? 'product' : 'products'} available
            </p>
          </Card>
        </aside>

        {/* Right: advert grid */}
        <div className="lg:col-span-2">
          <div className="mb-4">
            <h2 className="text-xl font-bold text-gray-800">
              Products from {vendor.business_name}
            </h2>
            <p className="text-sm text-gray-500">
              Everything this vendor is selling on FAZ Shop.
            </p>
          </div>

          {adverts.length === 0 ? (
            <EmptyState
              icon="📦"
              title="No products yet"
              description="This vendor hasn't published any products."
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {adverts.map((a) => (
                <Link key={a.id} to={`/advert/${a.id}`}>
                  <div className="group bg-white rounded-xl overflow-hidden border border-gray-200 hover:shadow-xl transition h-full flex flex-col">
                    <div className="aspect-[4/3] bg-gray-100 overflow-hidden">
                      {a.cover_image ? (
                        <img
                          src={resolveImageUrl(a.cover_image)}
                          alt={a.title}
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center text-4xl text-gray-300">
                          🛍️
                        </div>
                      )}
                      {a.is_premium && (
                        <span className="absolute top-2 left-2 bg-faz-orange text-white text-[10px] font-bold px-2 py-0.5 rounded-full uppercase">
                          Premium
                        </span>
                      )}
                    </div>
                    <div className="p-4 flex-1 flex flex-col">
                      <h3 className="font-semibold text-gray-800 line-clamp-2 mb-1">
                        {a.title}
                      </h3>
                      {a.location_name && (
                        <p className="text-xs text-gray-400 mb-2 flex items-center gap-1">
                          📍 {a.location_name}
                        </p>
                      )}
                      <div className="mt-auto flex justify-between items-center">
                        {a.price != null ? (
                          <span className="text-lg font-bold text-faz-green">
                            {a.currency} {Number(a.price).toFixed(2)}
                          </span>
                        ) : (
                          <span className="text-sm text-gray-400 italic">
                            Contact for price
                          </span>
                        )}
                        <span className="text-sm text-faz-orange font-medium group-hover:underline">
                          View →
                        </span>
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