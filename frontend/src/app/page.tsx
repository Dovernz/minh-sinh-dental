"use client";

import { useState, useEffect, useMemo } from 'react';
import axios from 'axios';

interface Clinic {
  id: number;
  name: string;
  address: string;
  hotline: string;
  total_chairs?: number;
  map_url?: string;
}

interface Service {
  id: number;
  name: string;
  category: string;
  duration_minutes: number;
}

interface PatientForm {
  fullName: string;
  phone: string;
  email: string;
  dob: string;
  service: number | '';
}

interface MatrixChair {
  chair: number;
  status: 'available' | 'booked';
  booking_id: number | null;
  customer_name: string | null;
  service_name: string | null;
}

interface MatrixRow {
  time: string;
  start_time: string;
  chairs: MatrixChair[];
}

export default function Home() {
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(true);
  
  // Data
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  
  // State: Bước 1
  const [selectedClinic, setSelectedClinic] = useState<number | null>(null);
  
  // State: Bước 2
  const [numPatients, setNumPatients] = useState<number>(1);
  const [patients, setPatients] = useState<PatientForm[]>([
    { fullName: '', phone: '', email: '', dob: '', service: '' }
  ]);
  
  // State: Bước 3
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');
  
  // State: Matrix & Booking
  const [matrixData, setMatrixData] = useState<MatrixRow[]>([]);
  const [myBookingIds, setMyBookingIds] = useState<number[]>([]);
  const [bookingSuccess, setBookingSuccess] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clinicRes, serviceRes] = await Promise.all([
          axios.get('http://localhost:8000/api/clinics/'),
          axios.get('http://localhost:8000/api/services/')
        ]);
        setClinics(clinicRes.data);
        setServices(serviceRes.data);
      } catch (error) {
        console.error("Lỗi khi tải dữ liệu API:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    
    const today = new Date().toISOString().split('T')[0];
    setSelectedDate(today);
  }, []);

  // Gọi API lấy ma trận ghế khi đổi ngày hoặc cơ sở
  useEffect(() => {
    if (selectedClinic && selectedDate) {
      axios.get(`http://localhost:8000/api/daily-schedule/?clinic_id=${selectedClinic}&date=${selectedDate}`)
        .then(res => setMatrixData(res.data))
        .catch(err => console.error(err));
    }
  }, [selectedClinic, selectedDate, bookingSuccess]);

  // Update mảng form dựa trên số lượng khách
  useEffect(() => {
    const currentLength = patients.length;
    if (numPatients > currentLength) {
      const newPatients = [...patients];
      for (let i = currentLength; i < numPatients; i++) {
        newPatients.push({ fullName: '', phone: '', email: '', dob: '', service: '' });
      }
      setPatients(newPatients);
    } else if (numPatients < currentLength && numPatients > 0) {
      setPatients(patients.slice(0, numPatients));
    }
  }, [numPatients]);

  const handlePatientChange = (index: number, field: keyof PatientForm, value: string | number) => {
    const updated = [...patients];
    updated[index] = { ...updated[index], [field]: value };
    setPatients(updated);
  };

  const handleBookingSubmit = async () => {
    if (!selectedClinic || !selectedDate || !selectedTime) {
      alert("Vui lòng chọn đầy đủ Khung giờ trước khi hoàn tất!");
      return;
    }
    
    const isValid = patients.every(p => p.fullName.trim() !== '' && p.phone.trim() !== '' && p.service !== '');
    if (!isValid) {
      alert("Vui lòng điền đủ Họ tên, SĐT và chọn Dịch vụ cho tất cả các khách hàng!");
      return;
    }
    
    const isValidPhone = patients.every(p => p.phone.length === 10 || p.phone.length === 11);
    if (!isValidPhone) {
      alert("Số điện thoại không hợp lệ! Vui lòng nhập từ 10 đến 11 chữ số.");
      return;
    }

    try {
      const payload = {
        clinic_id: selectedClinic,
        date: selectedDate,
        start_time: selectedTime,
        patients: patients.map(p => ({
          ...p,
          dob: p.dob ? `${p.dob}-01-01` : ''
        }))
      };
      
      const res = await axios.post('http://localhost:8000/api/bookings/', payload);
      
      if (res.status === 201) {
        setMyBookingIds(res.data.booking_ids);
        setBookingSuccess(true);
        alert('Đặt lịch thành công! Bạn có thể xem lại sơ đồ ghế bên dưới.');
      }
    } catch (error: any) {
      alert("Lỗi đặt lịch: " + (error.response?.data?.error || "Vui lòng thử lại"));
    }
  };

  const maxChairs = matrixData.length > 0 ? matrixData[0].chairs.length : 0;

  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center p-8">
      <div className="w-full max-w-6xl">
        <h1 className="text-3xl font-bold text-center text-blue-700 mb-10">Đặt Lịch Khám Nha Khoa</h1>
        
        {/* ================= BƯỚC 1: Chọn Chi Nhánh ================= */}
        {currentStep === 1 && (
        <div className="mb-8 transition-all">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold text-gray-800">Bước 1: Lựa chọn cơ sở (Chi nhánh)</h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {clinics.map((clinic) => (
              <div 
                key={clinic.id}
                onClick={() => setSelectedClinic(clinic.id)}
                className={`
                  p-6 rounded-2xl shadow-sm border-2 cursor-pointer transition-all duration-200 bg-white
                  ${selectedClinic === clinic.id 
                    ? 'border-blue-500 ring-4 ring-blue-100 bg-blue-50/30' 
                    : 'border-transparent hover:border-gray-200'
                  }
                `}
              >
                <h3 className="text-lg font-bold text-gray-900 mb-3">{clinic.name}</h3>
                <div className="text-sm text-gray-600 mb-2">{clinic.address}</div>
                <div className="text-sm text-gray-600">{clinic.hotline}</div>
              </div>
            ))}
          </div>

          {selectedClinic && (
            <div className="animate-fade-in-up bg-white rounded-2xl p-6 shadow-sm border border-gray-100 mb-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Bản đồ vị trí cơ sở</h3>
              {clinics.find(c => c.id === selectedClinic) && (
                <div className="rounded-xl overflow-hidden border border-gray-200 shadow-sm relative h-80">
                  {/* Sử dụng iframe tìm kiếm động theo địa chỉ */}
                  <iframe 
                    width="100%" 
                    height="100%" 
                    frameBorder="0" 
                    scrolling="no" 
                    marginHeight={0} 
                    marginWidth={0} 
                    src={`https://maps.google.com/maps?q=${encodeURIComponent(clinics.find(c => c.id === selectedClinic)?.address || '')}&t=&z=16&ie=UTF8&iwloc=&output=embed`}
                  ></iframe>
                </div>
              )}
              {clinics.find(c => c.id === selectedClinic)?.map_url && (
                <div className="mt-4 text-right">
                  <a href={clinics.find(c => c.id === selectedClinic)?.map_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 font-medium hover:underline inline-flex items-center">
                    Mở trên Google Maps ứng dụng
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                  </a>
                </div>
              )}
            </div>
          )}

          {selectedClinic && (
            <div className="flex justify-end">
              <button 
                onClick={() => setCurrentStep(2)}
                className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors"
              >
                Tiếp tục
              </button>
            </div>
          )}
        </div>
        )}


        {/* ================= BƯỚC 2: Nhập số lượng và form ================= */}
        {currentStep === 2 && (
          <div className="mb-8 animate-fade-in-up transition-all">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-800">Bước 2: Thông tin Khách hàng</h2>
            </div>

            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">Số lượng người khám</label>
              <input 
                type="number" min="1" max="10"
                value={numPatients}
                onChange={(e) => setNumPatients(parseInt(e.target.value) || 1)}
                className="w-32 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>

            <div className="space-y-6">
              {patients.map((p, index) => (
                <div key={index} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 relative">
                  <div className="absolute -top-3 -left-3 bg-blue-600 text-white w-8 h-8 flex items-center justify-center rounded-full font-bold shadow-md">
                    {index + 1}
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-2">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Họ và tên *</label>
                      <input type="text" value={p.fullName} onChange={(e) => handlePatientChange(index, 'fullName', e.target.value)} className="w-full px-4 py-2 border rounded-lg outline-none focus:border-blue-500" placeholder="VD: Nguyễn Văn A"/>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Số điện thoại *</label>
                      <input 
                        type="text" 
                        value={p.phone} 
                        onChange={(e) => {
                          const numericValue = e.target.value.replace(/\D/g, ''); // Xóa mọi ký tự không phải số
                          if (numericValue.length <= 11) {
                            handlePatientChange(index, 'phone', numericValue);
                          }
                        }} 
                        className="w-full px-4 py-2 border rounded-lg outline-none focus:border-blue-500" 
                        placeholder="VD: 0987654321"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                      <input type="email" value={p.email} onChange={(e) => handlePatientChange(index, 'email', e.target.value)} className="w-full px-4 py-2 border rounded-lg outline-none focus:border-blue-500"/>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">Năm sinh</label>
                      <input 
                        type="number" 
                        min="1900"
                        max={new Date().getFullYear()}
                        value={p.dob} 
                        onChange={(e) => handlePatientChange(index, 'dob', e.target.value)} 
                        className="w-full px-4 py-2 border rounded-lg outline-none focus:border-blue-500"
                        placeholder="VD: 1990"
                      />
                    </div>
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">Dịch vụ cần khám *</label>
                      <select 
                        value={p.service} 
                        onChange={(e) => handlePatientChange(index, 'service', parseInt(e.target.value) || '')} 
                        className="w-full px-4 py-2 border rounded-lg outline-none focus:border-blue-500 bg-white"
                      >
                        <option value="" disabled>-- Chọn dịch vụ --</option>
                        {services.map(s => (
                          <option key={s.id} value={s.id}>{s.name} ({s.duration_minutes} phút)</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 flex justify-between">
              <button 
                onClick={() => setCurrentStep(1)}
                className="px-8 py-3 bg-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-300 transition-colors"
              >
                Quay lại
              </button>
              <button 
                onClick={() => setCurrentStep(3)}
                className="px-8 py-3 bg-blue-600 text-white font-semibold rounded-xl hover:bg-blue-700 transition-colors"
              >
                Tiếp tục
              </button>
            </div>
          </div>
        )}

        {/* ================= BƯỚC 3: Chọn ngày giờ và Ma trận lưới ================= */}
        {currentStep === 3 && (
          <div className="mb-8 animate-fade-in-up">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Bước 3: Chọn Ngày Giờ Khám</h2>
            
            <div className="bg-white p-6 md:p-8 rounded-2xl shadow-sm border border-gray-100 mb-8">
              <div className="mb-6 max-w-sm">
                <label className="block text-sm font-medium text-gray-700 mb-2">Ngày khám</label>
                <input 
                  type="date" 
                  value={selectedDate}
                  onChange={(e) => {
                    setSelectedDate(e.target.value);
                    setSelectedTime(''); // Reset time when date changes
                  }}
                  className="w-full px-4 py-3 border rounded-xl outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
                />
              </div>

              {/* Ma trận Grid Trực tiếp */}
              <div>
                <h3 className="text-lg font-medium text-gray-800 mb-4">Sơ đồ Khung giờ và Phân bổ Ghế ngồi</h3>
                <p className="text-sm text-gray-500 mb-4">Nhấp vào một khung giờ bên dưới để đặt lịch. Các ghế màu xanh lam nhạt hiển thị vị trí dự kiến của bạn.</p>
                
                <div className="mb-4 flex flex-wrap gap-4 text-sm font-medium bg-gray-50 p-3 rounded-lg">
                  <div className="flex items-center"><div className="w-4 h-4 bg-green-100 border border-green-300 rounded mr-2"></div> Trống</div>
                  <div className="flex items-center"><div className="w-4 h-4 bg-gray-200 border border-gray-300 rounded mr-2"></div> Đã có người đặt</div>
                  {!bookingSuccess && <div className="flex items-center"><div className="w-4 h-4 bg-blue-200 border border-blue-400 rounded mr-2"></div> Đang chọn (Dự kiến)</div>}
                  {bookingSuccess && <div className="flex items-center"><div className="w-4 h-4 bg-blue-600 rounded mr-2"></div> Đã đặt thành công</div>}
                </div>

                <div className="overflow-x-auto rounded-xl border border-gray-200 shadow-sm">
                  <div className="min-w-max">
                    <div className="flex bg-gray-100 border-b border-gray-200">
                      <div className="w-28 shrink-0 p-4 font-bold text-gray-700 border-r border-gray-200 text-center">Khung giờ</div>
                      {Array.from({ length: maxChairs }).map((_, i) => (
                        <div key={i} className="flex-1 p-4 font-bold text-gray-700 text-center border-r border-gray-200 last:border-0 min-w-[150px]">
                          Ghế {i + 1}
                        </div>
                      ))}
                    </div>

                    {matrixData.map((row) => {
                      const availableChairs = row.chairs.filter(c => c.status === 'available');
                      // Nếu khách chọn giờ này, các ghế được xem trước sẽ là `numPatients` ghế trống đầu tiên
                      const previewChairIds = (selectedTime === row.start_time && !bookingSuccess)
                        ? availableChairs.slice(0, numPatients).map(c => c.chair)
                        : [];
                      
                      const isRowSelected = selectedTime === row.start_time;
                      const hasEnoughSpace = availableChairs.length >= numPatients;

                      return (
                        <div 
                          key={row.start_time} 
                          onClick={() => {
                            if (!bookingSuccess && hasEnoughSpace) setSelectedTime(row.start_time);
                          }}
                          className={`
                            flex border-b border-gray-200 last:border-0 transition-colors 
                            ${bookingSuccess ? '' : hasEnoughSpace ? 'cursor-pointer hover:bg-blue-50/30' : 'opacity-70 bg-gray-50'}
                            ${isRowSelected ? 'bg-blue-50/50' : ''}
                          `}
                        >
                          <div className={`w-28 shrink-0 p-4 font-bold border-r border-gray-200 flex items-center justify-center ${isRowSelected ? 'text-blue-700' : 'text-gray-600'}`}>
                            {row.start_time}
                          </div>
                          
                          {row.chairs.map((c) => {
                            const isMyBooking = c.booking_id && myBookingIds.includes(c.booking_id);
                            const isPreview = previewChairIds.includes(c.chair);
                            
                            let bgClass = "bg-green-100/50 text-green-800";
                            let content = <div className="text-sm font-medium">Trống</div>;

                            if (isMyBooking) {
                              bgClass = "bg-blue-600 text-white shadow-inner";
                              content = (
                                <>
                                  <div className="font-bold text-sm truncate w-full">{c.customer_name}</div>
                                  <div className="text-xs opacity-90 truncate w-full">{c.service_name}</div>
                                </>
                              );
                            } else if (isPreview) {
                              bgClass = "bg-blue-200 border-2 border-blue-400 text-blue-900";
                              content = <div className="text-sm font-bold">Lịch của bạn</div>;
                            } else if (c.status === 'booked') {
                              bgClass = "bg-gray-200 text-gray-500 cursor-not-allowed";
                              content = <div className="text-xs italic">Kín lịch</div>;
                            }

                            return (
                              <div key={c.chair} className="flex-1 border-r border-gray-200 last:border-0 p-2 min-w-[150px]">
                                <div className={`h-full w-full rounded-lg flex flex-col items-center justify-center p-2 text-center transition-all min-h-[60px] ${bgClass}`}>
                                  {content}
                                </div>
                              </div>
                            )
                          })}
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-between">
              <button 
                onClick={() => {
                  if (bookingSuccess) window.location.reload();
                  else setCurrentStep(2);
                }}
                className="px-8 py-3 bg-gray-200 text-gray-700 font-semibold rounded-xl hover:bg-gray-300 transition-colors"
              >
                {bookingSuccess ? 'Quay về trang chủ' : 'Quay lại'}
              </button>
              
              {!bookingSuccess && (
                <button 
                  onClick={handleBookingSubmit}
                  disabled={!selectedTime}
                  className={`px-10 py-4 font-bold text-lg rounded-xl shadow-lg transition-all duration-200
                    ${selectedTime 
                      ? 'bg-green-600 text-white hover:bg-green-700 hover:shadow-xl' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    }
                  `}
                >
                  Hoàn tất Đặt lịch
                </button>
              )}
            </div>
          </div>
        )}

      </div>
    </main>
  );
}
