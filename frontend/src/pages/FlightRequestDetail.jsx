import { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import { FaSpinner, FaArrowLeft, FaPrint, FaDownload, FaMoneyBillWave, FaCheckCircle, FaFileAlt } from 'react-icons/fa';
import toast from 'react-hot-toast';
import html2pdf from 'html2pdf.js';

const FlightRequestDetail = () => {
  const { id } = useParams();
  const [request, setRequest] = useState(null);
  const [loading, setLoading] = useState(true);
  const pdfContentRef = useRef();

  useEffect(() => {
    api.get(`/api/flight/request/${id}`)
      .then(res => setRequest(res.data))
      .catch(err => toast.error('Failed to load flight details'))
      .finally(() => setLoading(false));
  }, [id]);

  const handlePrint = () => window.print();
  const handlePDF = async () => {
    if (!pdfContentRef.current) return;
    const opt = {
      margin: [0.5, 0.5, 0.5, 0.5],
      filename: `FlightRequest_${request.request_reference}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'in', format: 'a4', orientation: 'portrait' }
    };
    await html2pdf().set(opt).from(pdfContentRef.current).save();
    toast.success('PDF downloaded!');
  };

  // Helper to get full file URL
  const getFileUrl = (filePath) => {
    if (!filePath) return null;
    if (filePath.startsWith('http://') || filePath.startsWith('https://')) return filePath;
    const base = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    return `${base}/${filePath}`;
  };

  if (loading) return <div className="flex justify-center py-12"><FaSpinner className="animate-spin text-brand-red text-4xl" /></div>;
  if (!request) return <div className="text-center py-12">Flight request not found</div>;

  // Safe check for documents
  const hasDocuments = !!request.passport_file || !!request.visa_file;

  const isPaid = request.payment_status === 'paid';

  return (
    <div className="container mx-auto px-4 py-12 max-w-4xl">
      <div className="flex justify-between items-center mb-6 no-print">
        <Link to="/my-flights" className="btn-outline py-2 px-4 flex items-center gap-2">
          <FaArrowLeft /> Back to My Flights
        </Link>
        <div className="flex gap-2">
          <button onClick={handlePrint} className="btn-outline py-2 px-4"><FaPrint /> Print</button>
          <button onClick={handlePDF} className="btn-outline py-2 px-4"><FaDownload /> PDF</button>
        </div>
      </div>

      <div ref={pdfContentRef} className="print-container">
        <div className="glass-card p-8">
          <div className="text-center border-b pb-4 mb-6">
            <h1 className="text-3xl font-black text-brand-red">Flight Booking Request</h1>
            <p>Reference: {request.request_reference}</p>
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            <div className="border rounded-lg p-4">
              <h3 className="font-bold mb-2">Passenger Details</h3>
              <p><strong>Name:</strong> {request.full_name}</p>
              <p><strong>Passport:</strong> {request.passport_number}</p>
              <p><strong>Nationality:</strong> {request.nationality}</p>
              <p><strong>Date of Birth:</strong> {new Date(request.date_of_birth).toLocaleDateString()}</p>
              <p><strong>Gender:</strong> {request.gender}</p>
            </div>
            <div className="border rounded-lg p-4">
              <h3 className="font-bold mb-2">Contact</h3>
              <p><strong>Phone:</strong> {request.phone}</p>
              <p><strong>Email:</strong> {request.email}</p>
              <p><strong>Address:</strong> {request.address || 'N/A'}</p>
            </div>
          </div>

          <div className="border rounded-lg p-4 mt-4">
            <h3 className="font-bold mb-2">Flight Details</h3>
            <p><strong>Airline:</strong> {request.airline_name || request.airline_id || 'N/A'}</p>
            <p><strong>Origin:</strong> {request.origin}</p>
            <p><strong>Destination:</strong> {request.destination}</p>
            <p><strong>Outbound Date:</strong> {new Date(request.travel_date).toLocaleDateString()}</p>
            <p><strong>Return Date:</strong> {request.return_date ? new Date(request.return_date).toLocaleDateString() : 'N/A'}</p>
            <p><strong>Class:</strong> {request.travel_class}</p>
            <p><strong>Passengers:</strong> {request.passengers}</p>
          </div>

          <div className="border rounded-lg p-4 mt-4">
            <h3 className="font-bold mb-2">Additional Options</h3>
            <p><strong>Meal:</strong> {request.meal_preference || 'Standard'}</p>
            <p><strong>Seat:</strong> {request.seat_preference || 'No preference'}</p>
            <p><strong>Assistance:</strong> {request.special_assistance || 'None'}</p>
          </div>

          {/* Documents Section */}
          {hasDocuments && (
            <div className="border rounded-lg p-4 mt-4">
              <h3 className="font-bold mb-2">Uploaded Documents</h3>
              <div className="space-y-2">
                {request.passport_file && (
                  <div><FaFileAlt className="inline mr-2" /> <a href={getFileUrl(request.passport_file)} target="_blank" rel="noopener noreferrer" className="text-brand-red underline">Passport Copy</a></div>
                )}
                {request.visa_file && (
                  <div><FaFileAlt className="inline mr-2" /> <a href={getFileUrl(request.visa_file)} target="_blank" rel="noopener noreferrer" className="text-brand-red underline">Visa Copy</a></div>
                )}
              </div>
            </div>
          )}

          <div className="border rounded-lg p-4 mt-4">
            <h3 className="font-bold mb-2">Payment Summary</h3>
            <table className="w-full">
              <tbody>
                <tr className="border-b"><td className="py-2">Base Fare:</td><td className="text-right">ZMW {request.base_amount}</td></tr>
                <tr className="border-b"><td className="py-2">Service Fee:</td><td className="text-right">ZMW {request.service_fee}</td></tr>
                <tr><td className="py-2 font-bold">Total:</td><td className="text-right font-bold">ZMW {request.total_amount}</td></tr>
              </tbody>
            </table>
            <p className="mt-2"><strong>Payment Status:</strong> <span className={`inline-block px-2 py-1 rounded-full text-xs ${isPaid ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>{request.payment_status || 'pending'}</span></p>
          </div>

          {request.notes && (
            <div className="border rounded-lg p-4 mt-4">
              <h3 className="font-bold mb-2">Notes</h3>
              <p>{request.notes}</p>
            </div>
          )}
        </div>
      </div>

      {!isPaid && (
        <div className="mt-6 text-center no-print">
          <Link to={`/payment/flight/${request.id}`} className="btn-primary">
            <FaMoneyBillWave className="inline mr-2" /> Pay Now
          </Link>
        </div>
      )}
      {isPaid && <div className="mt-6 text-center text-green-600 font-bold"><FaCheckCircle className="inline mr-2" /> Payment completed</div>}
    </div>
  );
};

export default FlightRequestDetail;