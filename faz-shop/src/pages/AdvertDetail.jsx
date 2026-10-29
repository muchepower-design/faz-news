// src/pages/AdvertDetail.jsx
import { useEffect, useState } from 'react';
import { Link, useParams, useNavigate } from 'react-router-dom';
import { shopAPI } from '../api';
import { Card, Button, Badge, Spinner, EmptyState } from '../components/ui';
import { resolveImageUrl } from '../utils';
import { FaMapMarkerAlt, FaPhone, FaEnvelope, FaWhatsapp, FaPlay, FaTimes, FaArrowLeft } from 'react-icons/fa';

export default function AdvertDetail() {
  const { advertId } = useParams();
  const navigate = useNavigate();
  const [advert, setAdvert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeMedia, setActiveMedia] = useState(0);
  const [lightbox, setLightbox] = useState(null);

  useEffect(() => {
    setLoading(true);
    shopAPI.getAdvert(advertId)
      .then((res) => setAdvert(res.data))
      .catch(() => setAdvert(null))
      .finally(() => setLoading(false));
  }, [advertId]);

  if (loading) return <div className="flex justify-center py-32"><Spinner size="xl" /></div>;

  if (!advert) {
    return (
      <div className="container mx-auto px-4 py-20">
        <EmptyState
          icon="🔍"
          title="Product not found"
          description="This advert may have been removed or is no longer available."
          action={<Link to="/browse"><Button>Browse other products</Button></Link>}
        />
      </div>
    );
  }

  const media = advert.media || [];
  const currentMedia = media[activeMedia];
  const vendor = advert.vendor;

  return (
    <div className="container mx-auto px-4 py-8">
      <Link to="/browse" className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-faz-orange mb-4">
        <FaArrowLeft /> Back to browse
      </Link>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Media */}
        <div>
          <div className="bg-gray-100 rounded-2xl overflow-hidden aspect-square relative cursor-zoom-in"
               onClick={() => currentMedia && setLightbox(currentMedia)}>
            {currentMedia ? (
              currentMedia.media_type === 'video' ? (
                <video src={resolveImageUrl(currentMedia.url)} controls className="w-full h-full object-contain" />
              ) : (
                <img src={resolveImageUrl(currentMedia.url)} alt={advert.title} className="w-full h-full object-cover" />
              )
            ) : (
              <div className="w-full h-full flex items-center justify-center text-8xl text-gray-300">🛍️</div>
            )}
          </div>

          {media.length > 1 && (
            <div className="flex gap-2 mt-3 overflow-x-auto pb-2">
              {media.map((m, i) => (
                <button key={m.id} onClick={() => setActiveMedia(i)}
                  className={`flex-shrink-0 w-20 h-20 rounded-lg overflow-hidden border-2 transition ${i === activeMedia ? 'border-faz-orange' : 'border-gray-200'}`}>
                  {m.media_type === 'video' ? (
                    <div className="w-full h-full bg-gray-900 flex items-center justify-center text-white">
                      <FaPlay />
                    </div>
                  ) : (
                    <img src={resolveImageUrl(m.url)} alt="" className="w-full h-full object-cover" />
                  )}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Info + Buy */}
        <div>
          <div className="flex items-center gap-2 mb-2">
            {advert.is_premium && <Badge variant="orange">Premium</Badge>}
            {advert.category && <Badge>{advert.category.icon} {advert.category.name}</Badge>}
          </div>

          <h1 className="text-3xl font-bold text-gray-800 mb-3">{advert.title}</h1>

          {advert.price != null ? (
            <div className="mb-4">
              <span className="text-4xl font-bold text-faz-green">{advert.currency} {Number(advert.price).toFixed(2)}</span>
            </div>
          ) : (
            <div className="mb-4 text-2xl font-semibold text-gray-500 italic">Contact vendor for price</div>
          )}

          {advert.location_name && (
            <p className="text-sm text-gray-600 mb-4 flex items-center gap-2">
              <FaMapMarkerAlt className="text-faz-orange" /> {advert.location_name}
            </p>
          )}

          <div className="prose prose-sm max-w-none text-gray-700 mb-6 whitespace-pre-wrap">
            {advert.description}
          </div>

          {/* Buy */}
          <Card padding="md" className="mb-6">
            <h3 className="font-semibold text-gray-800 mb-3">Purchase</h3>
            <div className="flex flex-col sm:flex-row gap-2">
              <Button onClick={() => navigate(`/checkout/${advert.id}`)} size="lg" className="flex-1">
                Buy Now
              </Button>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              {advert.payment_method === 'offline' && 'Pay the vendor directly (bank or mobile money).'}
              {advert.payment_method === 'system' && 'Pay securely through the FAZ platform.'}
              {advert.payment_method === 'both' && 'Choose to pay via FAZ platform or directly to the vendor at checkout.'}
            </p>
          </Card>

          {/* Vendor */}
          {vendor && (
            <Card padding="md">
              <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">Sold by</h3>
              <Link to={`/vendor/${vendor.id}`} className="flex items-center gap-3 hover:bg-gray-50 rounded-lg p-2 -m-2 transition">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-faz-green to-faz-orange overflow-hidden flex items-center justify-center text-white font-bold">
                  {vendor.logo_url ? (
                    <img src={resolveImageUrl(vendor.logo_url)} alt="" className="w-full h-full object-cover" />
                  ) : (
                    vendor.business_name?.[0]
                  )}
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-gray-800">{vendor.business_name}</p>
                  {vendor.location_name && <p className="text-xs text-gray-500">{vendor.location_name}</p>}
                </div>
              </Link>

              <div className="mt-4 space-y-1 text-sm">
                {vendor.contact_phone && (
                  <a href={`tel:${vendor.contact_phone}`} className="flex items-center gap-2 text-gray-600 hover:text-faz-orange">
                    <FaPhone /> {vendor.contact_phone}
                  </a>
                )}
                {vendor.contact_email && (
                  <a href={`mailto:${vendor.contact_email}`} className="flex items-center gap-2 text-gray-600 hover:text-faz-orange">
                    <FaEnvelope /> {vendor.contact_email}
                  </a>
                )}
                {vendor.contact_whatsapp && (
                  <a href={`https://wa.me/${vendor.contact_whatsapp.replace(/\D/g, '')}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 text-gray-600 hover:text-green-600">
                    <FaWhatsapp /> WhatsApp
                  </a>
                )}
              </div>
            </Card>
          )}
        </div>
      </div>

      {/* Lightbox */}
      {lightbox && lightbox.media_type === 'image' && (
        <div className="fixed inset-0 z-50 bg-black/95 flex items-center justify-center p-4" onClick={() => setLightbox(null)}>
          <button onClick={() => setLightbox(null)} className="absolute top-4 right-4 text-white text-3xl p-2 hover:bg-white/10 rounded-full">
            <FaTimes />
          </button>
          <img src={resolveImageUrl(lightbox.url)} alt="" className="max-w-full max-h-full object-contain" onClick={(e) => e.stopPropagation()} />
        </div>
      )}
    </div>
  );
}