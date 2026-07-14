import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';
import PriceCalculator from '../components/PriceCalculator';

const FlightRequest = () => {
  const navigate = useNavigate();
  const [airlines, setAirlines] = useState([]);
  const [loading, setLoading] = useState(false);
  const [priceAvailable, setPriceAvailable] = useState(null);
  const [calculatedPrice, setCalculatedPrice] = useState(null);
  const [files, setFiles] = useState({ passport: null, visa: null });

  const [formData, setFormData] = useState({
    action_type: 'quote',
    // Personal details
    full_name: '',
    passport_number: '',
    passport_expiry: '',
    nationality: '',
    date_of_birth: '',
    gender: 'male',
    // Contact
    phone: '',
    email: '',
    address: '',
    // Flight details
    airline_id: '',
    origin: '',
    destination: '',
    travel_date: '',
    return_date: '',
    travel_class: 'economy',
    passengers: 1,
    // Additional services
    meal_preference: 'standard',
    seat_preference: 'window',
    special_assistance: '',
    // Internal
    notes: '',
    base_amount: 0
  });

  // Fetch airlines on mount
  useEffect(() => {
    api.get('/api/pricing/airlines')
      .then(res => setAirlines(res.data))
      .catch(err => console.error('Failed to load airlines', err));
  }, []);

  const handlePriceFetched = (amount) => {
    setCalculatedPrice(amount);
    setPriceAvailable(amount !== null);
    if (amount !== null) {
      setFormData(prev => ({ ...prev, base_amount: amount }));
    }
  };

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (file) {
      setFiles(prev => ({ ...prev, [type]: file }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    // Build payload
    const payload = {
      ...formData,
      service_type: 'flight_ticketing',
      email: formData.email || null,
      travel_date: formData.travel_date ? new Date(formData.travel_date).toISOString() : null,
      return_date: formData.return_date ? new Date(formData.return_date).toISOString() : null,
      passengers: parseInt(formData.passengers, 10),
      base_amount: calculatedPrice || parseFloat(formData.base_amount) || 0,
      notes: formData.notes || null,
      // Pass extra fields as JSON in a separate field (service_data)
      service_data: {
        passport_number: formData.passport_number,
        passport_expiry: formData.passport_expiry,
        nationality: formData.nationality,
        date_of_birth: formData.date_of_birth,
        gender: formData.gender,
        address: formData.address,
        meal_preference: formData.meal_preference,
        seat_preference: formData.seat_preference,
        special_assistance: formData.special_assistance,
      }
    };

    try {
      // Submit as multipart/form-data if we have files
      if (files.passport || files.visa) {
        const formDataObj = new FormData();
        // Append all fields as JSON
        formDataObj.append('data', JSON.stringify(payload));
        if (files.passport) formDataObj.append('passport', files.passport);
        if (files.visa) formDataObj.append('visa', files.visa);
        const res = await api.post('/api/flight/request', formDataObj, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
        toast.success('Flight request submitted!');
        if (priceAvailable && formData.action_type !== 'quote') {
          navigate(`/payment/flight/${res.data.id}`);
        } else {
          navigate('/dashboard');
        }
      } else {
        const res = await api.post('/api/flight/request', payload);
        toast.success('Flight request submitted!');
        if (priceAvailable && formData.action_type !== 'quote') {
          navigate(`/payment/flight/${res.data.id}`);
        } else {
          navigate('/dashboard');
        }
      }
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) toast.error(detail.map(e => e.msg).join(', '));
      else if (typeof detail === 'string') toast.error(detail);
      else toast.error('Failed to submit');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <div className="glass-card p-8">
        <h1 className="text-3xl font-black mb-6">Flight Booking Request</h1>
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Personal Information */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Passenger Details</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">Full Name (as per passport) *</label><input type="text" required className="w-full p-2 border rounded" value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Passport Number *</label><input type="text" required className="w-full p-2 border rounded" value={formData.passport_number} onChange={e => setFormData({...formData, passport_number: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Passport Expiry Date *</label><input type="date" required className="w-full p-2 border rounded" value={formData.passport_expiry} onChange={e => setFormData({...formData, passport_expiry: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Nationality *</label><input type="text" required className="w-full p-2 border rounded" value={formData.nationality} onChange={e => setFormData({...formData, nationality: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Date of Birth *</label><input type="date" required className="w-full p-2 border rounded" value={formData.date_of_birth} onChange={e => setFormData({...formData, date_of_birth: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Gender *</label><select className="w-full p-2 border rounded" value={formData.gender} onChange={e => setFormData({...formData, gender: e.target.value})}><option value="male">Male</option><option value="female">Female</option><option value="other">Other</option></select></div>
            </div>
          </fieldset>

          {/* Contact Details */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Contact Information</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">Phone *</label><input type="tel" required className="w-full p-2 border rounded" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Email *</label><input type="email" required className="w-full p-2 border rounded" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} /></div>
              <div className="md:col-span-2"><label className="block font-bold mb-1">Address</label><input type="text" className="w-full p-2 border rounded" value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} /></div>
            </div>
          </fieldset>

          {/* Flight Details */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Flight Details</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">Airline *</label>
                <select className="w-full p-2 border rounded" value={formData.airline_id} onChange={e => setFormData({...formData, airline_id: e.target.value})}>
                  <option value="">Select Airline</option>
                  {airlines.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}
                </select>
              </div>
              <div><label className="block font-bold mb-1">Travel Class *</label>
                <select className="w-full p-2 border rounded" value={formData.travel_class} onChange={e => setFormData({...formData, travel_class: e.target.value})}>
                  <option value="economy">Economy</option>
                  <option value="business">Business</option>
                  <option value="first">First</option>
                </select>
              </div>
              <div><label className="block font-bold mb-1">Origin (Airport/City) *</label><input type="text" required className="w-full p-2 border rounded" value={formData.origin} onChange={e => setFormData({...formData, origin: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Destination *</label><input type="text" required className="w-full p-2 border rounded" value={formData.destination} onChange={e => setFormData({...formData, destination: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Outbound Date *</label><input type="date" required className="w-full p-2 border rounded" value={formData.travel_date} onChange={e => setFormData({...formData, travel_date: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Return Date</label><input type="date" className="w-full p-2 border rounded" value={formData.return_date} onChange={e => setFormData({...formData, return_date: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Passengers *</label><input type="number" min="1" required className="w-full p-2 border rounded" value={formData.passengers} onChange={e => setFormData({...formData, passengers: e.target.value})} /></div>
            </div>
          </fieldset>

          {/* Additional Services */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Additional Options</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">Meal Preference</label>
                <select className="w-full p-2 border rounded" value={formData.meal_preference} onChange={e => setFormData({...formData, meal_preference: e.target.value})}>
                  <option value="standard">Standard</option>
                  <option value="vegetarian">Vegetarian</option>
                  <option value="vegan">Vegan</option>
                  <option value="halal">Halal</option>
                  <option value="kosher">Kosher</option>
                  <option value="diabetic">Diabetic</option>
                </select>
              </div>
              <div><label className="block font-bold mb-1">Seat Preference</label>
                <select className="w-full p-2 border rounded" value={formData.seat_preference} onChange={e => setFormData({...formData, seat_preference: e.target.value})}>
                  <option value="window">Window</option>
                  <option value="aisle">Aisle</option>
                  <option value="middle">Middle</option>
                  <option value="no_preference">No Preference</option>
                </select>
              </div>
              <div className="md:col-span-2"><label className="block font-bold mb-1">Special Assistance</label><input type="text" className="w-full p-2 border rounded" value={formData.special_assistance} onChange={e => setFormData({...formData, special_assistance: e.target.value})} placeholder="E.g., wheelchair, visual assistance, etc." /></div>
            </div>
          </fieldset>

          {/* Price Calculator */}
          <PriceCalculator
            serviceType="flight"
            params={{
              airline_id: formData.airline_id,
              origin: formData.origin,
              destination: formData.destination,
              travel_class: formData.travel_class
            }}
            onPriceFetched={handlePriceFetched}
          />

          {/* File Uploads */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Document Upload</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">Passport Copy (PDF/Image)</label><input type="file" accept="image/*,application/pdf" onChange={(e) => handleFileChange(e, 'passport')} className="w-full p-2 border rounded" /></div>
              <div><label className="block font-bold mb-1">Visa Copy (if applicable)</label><input type="file" accept="image/*,application/pdf" onChange={(e) => handleFileChange(e, 'visa')} className="w-full p-2 border rounded" /></div>
            </div>
          </fieldset>

          {/* Internal Notes */}
          <div><label className="block font-bold mb-1">Internal Notes (for company use)</label><textarea className="w-full p-2 border rounded" rows="3" value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})} placeholder="Any internal remarks or special instructions" /></div>

          <button type="submit" disabled={loading} className="btn-primary w-full">
            {loading ? 'Submitting...' : (priceAvailable && formData.action_type !== 'quote' ? 'Proceed to Payment' : 'Request Quotation')}
          </button>
        </form>
      </div>
    </div>
  );
};

export default FlightRequest;