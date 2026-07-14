import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import toast from 'react-hot-toast';

const CarHireRequest = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [vehicleTypes, setVehicleTypes] = useState([]);
  const [files, setFiles] = useState({ license: null, id_document: null });

  const [idType, setIdType] = useState('nrc'); // 'nrc' or 'passport'
  const [idNumber, setIdNumber] = useState('');
  const [nationality, setNationality] = useState('');
  const [nationalityLocked, setNationalityLocked] = useState(false);
  const nrcInputRef = useRef(null);

  const [formData, setFormData] = useState({
    action_type: 'quote',
    full_name: '',
    phone: '',
    email: '',
    driver_license_number: '',
    driver_license_expiry: '',
    date_of_birth: '',
    pickup_location: '',
    dropoff_location: '',
    pickup_date: '',
    pickup_time: '',
    dropoff_date: '',
    dropoff_time: '',
    rental_duration_days: '',
    vehicle_type: '',
    preferred_model: '',
    transmission: '',
    fuel_policy: 'Full-to-Full',
    additional_drivers: 0,
    child_seat: false,
    gps_navigation: false,
    base_amount: 0,
    notes: ''
  });

  // Fetch vehicle types on mount
  useEffect(() => {
    api.get('/api/pricing/vehicle-types')
      .then(res => setVehicleTypes(res.data))
      .catch(err => console.error('Failed to load vehicle types', err));
  }, []);

  // ---- ID validation functions ----
  const isValidNRC = (value) => {
    // Remove any slashes for validation
    const raw = value.replace(/\//g, '');
    // Format 1: "ZMB" followed by exactly 10 digits (total 13 characters)
    const nrcZmbRegex = /^ZMB\d{10}$/;
    // Format 2: 6 digits + 1-2 digits + 1-3 digits (e.g., 266817/24/1)
    const rawSlashRegex = /^\d{6}\d{1,2}\d{1,3}$/;
    return nrcZmbRegex.test(raw) || (rawSlashRegex.test(raw) && raw.length >= 8 && raw.length <= 11);
  };

  const isValidPassport = (value) => {
    // Accept any passport format: at least 6 characters, letters and numbers
    const passportRegex = /^[A-Z0-9]{6,20}$/;
    return passportRegex.test(value.toUpperCase());
  };

  const getNationalityFromNRC = (value) => {
    const raw = value.replace(/\//g, '');
    if (value.includes('/')) {
      const parts = value.split('/');
      const last = parts[parts.length - 1];
      if (last === '1') return 'Zambian';
      else return null;
    }
    if (value.startsWith('ZMB')) {
      return 'Zambian';
    }
    return null;
  };

  // ---- Format NRC input with slashes ----
  const formatNRC = (value) => {
    // Remove any non-digit and non-letter characters except ZMB prefix
    let raw = value.replace(/[^A-Za-z0-9]/g, '');
    // If it starts with ZMB, keep as is (no slashes) – allow up to 13 characters (ZMB + 10 digits)
    if (raw.toUpperCase().startsWith('ZMB')) {
      return raw.toUpperCase().slice(0, 13);
    }
    // Otherwise, treat as numeric with slashes
    raw = raw.slice(0, 11);
    let formatted = '';
    for (let i = 0; i < raw.length; i++) {
      if (i === 6) {
        formatted += '/';
      } else if (i === 8) {
        formatted += '/';
      }
      formatted += raw[i];
    }
    return formatted;
  };

  const handleIdNumberChange = (e) => {
    let value = e.target.value;
    // If NRC, format with slashes
    if (idType === 'nrc') {
      value = formatNRC(value);
    }
    setIdNumber(value);

    // Auto‑detect nationality for NRC
    if (idType === 'nrc' && value.length > 0) {
      const detected = getNationalityFromNRC(value);
      if (detected) {
        setNationality(detected);
        setNationalityLocked(true);
      } else {
        setNationality('');
        setNationalityLocked(false);
      }
    } else {
      // For passport, we don't auto‑detect
      setNationalityLocked(false);
    }
  };

  const handleIdTypeChange = (type) => {
    setIdType(type);
    setIdNumber('');
    setNationality('');
    setNationalityLocked(false);
  };

  const handleNationalityChange = (e) => {
    if (!nationalityLocked) {
      setNationality(e.target.value);
    }
  };

  const isFormValid = () => {
    if (!formData.full_name || !formData.phone || !formData.email) return false;
    if (!idNumber) return false;
    if (idType === 'nrc' && !isValidNRC(idNumber)) return false;
    if (idType === 'passport' && !isValidPassport(idNumber)) return false;
    if (!nationality) return false;
    if (!formData.driver_license_number || !formData.driver_license_expiry) return false;
    if (!formData.pickup_location || !formData.pickup_date) return false;
    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormValid()) {
      toast.error('Please fill all required fields correctly.');
      return;
    }

    setLoading(true);

    const payload = {
      ...formData,
      service_type: 'carhire',
      email: formData.email || null,
      id_type: idType,
      id_number: idNumber,
      nationality: nationality,
      driver_license_expiry: new Date(formData.driver_license_expiry).toISOString(),
      date_of_birth: formData.date_of_birth ? new Date(formData.date_of_birth).toISOString() : null,
      pickup_date: new Date(formData.pickup_date).toISOString(),
      dropoff_date: formData.dropoff_date ? new Date(formData.dropoff_date).toISOString() : null,
      base_amount: parseFloat(formData.base_amount) || 0,
      notes: formData.notes || null,
      rental_duration_days: formData.rental_duration_days ? parseInt(formData.rental_duration_days) : null,
      additional_drivers: parseInt(formData.additional_drivers) || 0,
    };

    try {
      const formDataObj = new FormData();
      formDataObj.append('data', JSON.stringify(payload));
      if (files.license) formDataObj.append('license_file', files.license);
      if (files.id_document) formDataObj.append('id_document', files.id_document);

      await api.post('/api/carhire/request', formDataObj, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      toast.success('Car hire request submitted!');
      navigate('/dashboard');
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        toast.error(detail.map(e => e.msg).join(', '));
      } else if (typeof detail === 'string') {
        toast.error(detail);
      } else {
        toast.error('Failed to submit');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e, type) => {
    const file = e.target.files[0];
    if (file) setFiles(prev => ({ ...prev, [type]: file }));
  };

  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <div className="glass-card p-8">
        <h1 className="text-3xl font-black mb-6">Car Hire / Rental Request</h1>
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Personal Details */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Personal Details</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">Full Name *</label><input type="text" required className="w-full p-2 border rounded" value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Phone *</label><input type="tel" required className="w-full p-2 border rounded" value={formData.phone} onChange={e => setFormData({...formData, phone: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Email *</label><input type="email" required className="w-full p-2 border rounded" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Date of Birth *</label><input type="date" required className="w-full p-2 border rounded" value={formData.date_of_birth} onChange={e => setFormData({...formData, date_of_birth: e.target.value})} /></div>
            </div>
          </fieldset>

          {/* Identification */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Identification</legend>
            <div className="space-y-4">
              <div>
                <label className="block font-bold mb-2">ID Type *</label>
                <div className="flex gap-6">
                  <label className="flex items-center gap-2">
                    <input type="radio" value="nrc" checked={idType === 'nrc'} onChange={() => handleIdTypeChange('nrc')} />
                    NRC (National Registration Card)
                  </label>
                  <label className="flex items-center gap-2">
                    <input type="radio" value="passport" checked={idType === 'passport'} onChange={() => handleIdTypeChange('passport')} />
                    Passport
                  </label>
                </div>
              </div>
              <div>
                <label className="block font-bold mb-1">{idType === 'nrc' ? 'NRC Number *' : 'Passport Number *'}</label>
                <input
                  ref={nrcInputRef}
                  type="text"
                  required
                  className="w-full p-2 border rounded font-mono"
                  value={idNumber}
                  onChange={handleIdNumberChange}
                  placeholder={idType === 'nrc' ? 'e.g., ZMB1234567890 or 266817/24/1' : 'e.g., ZA123456'}
                />
                {idType === 'nrc' && idNumber.length > 0 && !isValidNRC(idNumber) && (
                  <p className="text-red-500 text-sm mt-1">
                    Invalid NRC format. Use ZMB followed by 10 digits OR 6 digits/1-2 digits/1-3 digits.
                  </p>
                )}
                {idType === 'passport' && idNumber.length > 0 && !isValidPassport(idNumber) && (
                  <p className="text-red-500 text-sm mt-1">Invalid passport format. Enter at least 6 characters (letters and numbers).</p>
                )}
              </div>
              <div>
                <label className="block font-bold mb-1">Nationality *</label>
                <input
                  type="text"
                  required
                  className={`w-full p-2 border rounded ${nationalityLocked ? 'bg-gray-100 cursor-not-allowed' : ''}`}
                  value={nationality}
                  onChange={handleNationalityChange}
                  readOnly={nationalityLocked}
                  placeholder={nationalityLocked ? 'Auto-detected' : 'Enter nationality'}
                />
                {nationalityLocked && <p className="text-sm text-gray-500 mt-1">Nationality auto-detected from NRC and locked.</p>}
              </div>
            </div>
          </fieldset>

          {/* Driver License */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Driver License</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">License Number *</label><input type="text" required className="w-full p-2 border rounded" value={formData.driver_license_number} onChange={e => setFormData({...formData, driver_license_number: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Expiry Date *</label><input type="date" required className="w-full p-2 border rounded" value={formData.driver_license_expiry} onChange={e => setFormData({...formData, driver_license_expiry: e.target.value})} /></div>
            </div>
          </fieldset>

          {/* Rental Details */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Rental Details</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">Pickup Location *</label><input type="text" required className="w-full p-2 border rounded" value={formData.pickup_location} onChange={e => setFormData({...formData, pickup_location: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Drop-off Location</label><input type="text" className="w-full p-2 border rounded" value={formData.dropoff_location} onChange={e => setFormData({...formData, dropoff_location: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Pickup Date *</label><input type="date" required className="w-full p-2 border rounded" value={formData.pickup_date} onChange={e => setFormData({...formData, pickup_date: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Pickup Time</label><input type="time" className="w-full p-2 border rounded" value={formData.pickup_time} onChange={e => setFormData({...formData, pickup_time: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Drop-off Date</label><input type="date" className="w-full p-2 border rounded" value={formData.dropoff_date} onChange={e => setFormData({...formData, dropoff_date: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Drop-off Time</label><input type="time" className="w-full p-2 border rounded" value={formData.dropoff_time} onChange={e => setFormData({...formData, dropoff_time: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Rental Duration (days)</label><input type="number" min="1" className="w-full p-2 border rounded" value={formData.rental_duration_days} onChange={e => setFormData({...formData, rental_duration_days: e.target.value})} /></div>
            </div>
          </fieldset>

          {/* Vehicle Preferences */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Vehicle Preferences</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">Vehicle Type</label>
                <select className="w-full p-2 border rounded" value={formData.vehicle_type} onChange={e => setFormData({...formData, vehicle_type: e.target.value})}>
                  <option value="">Select Vehicle Type</option>
                  {vehicleTypes.map(type => <option key={type} value={type}>{type}</option>)}
                </select>
              </div>
              <div><label className="block font-bold mb-1">Preferred Model</label><input type="text" className="w-full p-2 border rounded" value={formData.preferred_model} onChange={e => setFormData({...formData, preferred_model: e.target.value})} /></div>
              <div><label className="block font-bold mb-1">Transmission</label>
                <select className="w-full p-2 border rounded" value={formData.transmission} onChange={e => setFormData({...formData, transmission: e.target.value})}>
                  <option value="">Any</option>
                  <option value="Automatic">Automatic</option>
                  <option value="Manual">Manual</option>
                </select>
              </div>
              <div><label className="block font-bold mb-1">Fuel Policy</label>
                <select className="w-full p-2 border rounded" value={formData.fuel_policy} onChange={e => setFormData({...formData, fuel_policy: e.target.value})}>
                  <option value="Full-to-Full">Full-to-Full</option>
                  <option value="Pre-paid">Pre-paid</option>
                </select>
              </div>
              <div><label className="block font-bold mb-1">Additional Drivers</label><input type="number" min="0" className="w-full p-2 border rounded" value={formData.additional_drivers} onChange={e => setFormData({...formData, additional_drivers: parseInt(e.target.value) || 0})} /></div>
              <div className="flex items-center gap-4"><label><input type="checkbox" checked={formData.child_seat} onChange={e => setFormData({...formData, child_seat: e.target.checked})} /> Child Seat</label><label><input type="checkbox" checked={formData.gps_navigation} onChange={e => setFormData({...formData, gps_navigation: e.target.checked})} /> GPS Navigation</label></div>
            </div>
          </fieldset>

          {/* Document Uploads */}
          <fieldset className="border rounded-lg p-4">
            <legend className="font-bold text-lg px-2">Upload Documents</legend>
            <div className="grid md:grid-cols-2 gap-4 mt-2">
              <div><label className="block font-bold mb-1">Driver License Copy *</label><input type="file" accept="image/*,application/pdf" required className="w-full p-2 border rounded" onChange={(e) => handleFileChange(e, 'license')} /></div>
              <div><label className="block font-bold mb-1">{idType === 'nrc' ? 'NRC Copy *' : 'Passport Copy *'}</label><input type="file" accept="image/*,application/pdf" required className="w-full p-2 border rounded" onChange={(e) => handleFileChange(e, 'id_document')} /></div>
            </div>
          </fieldset>

          <div><label className="block font-bold mb-1">Base Amount (ZMW)</label><input type="number" step="0.01" className="w-full p-2 border rounded" value={formData.base_amount} onChange={e => setFormData({...formData, base_amount: e.target.value})} /></div>
          <div><label className="block font-bold mb-1">Notes</label><textarea className="w-full p-2 border rounded" rows="3" value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})} /></div>

          <button type="submit" disabled={loading || !isFormValid()} className="btn-primary w-full">
            {loading ? 'Submitting...' : 'Submit Request'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CarHireRequest;