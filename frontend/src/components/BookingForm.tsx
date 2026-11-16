"use client";

import { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import axios from 'axios';

// --- CONSTANTS & TYPES ---
const SHOW_DOCTOR_SELECTION = false;

const DOCTORS = [
  { id: 1, name: "ThS.BS Nguyễn Minh Hải", title: "Chuyên gia Răng Hàm Mặt" },
  { id: 2, name: "BS. Lê Thị Hồng Nhung", title: "Chuyên gia Niềng Răng - Thẩm mỹ" },
  { id: 3, name: "BS. Trần Văn Nam", title: "Chuyên gia Cấy ghép Implant" }
];

const TIME_SLOTS = [
  "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
  "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
  "17:30", "18:00", "18:30", "19:00", "19:30"
];

interface Clinic {
  id?: number;
  clinic_id?: number;
  name: string;
  address: string;
  hotline?: string;
  phone?: string;
  total_chairs?: number;
  map_url?: string;
}

const DEFAULT_CLINICS: Clinic[] = [
  { id: 1, clinic_id: 1, name: 'Cơ sở 1 - Quán Sứ', address: '46C Quán Sứ, Hoàn Kiếm, Hà Nội', hotline: '0981 123 456', phone: '0981 123 456' },
  { id: 2, clinic_id: 2, name: 'Cơ sở 2 - Ngọc Lâm', address: '376 - 380 Ngọc Lâm, Long Biên, Hà Nội', hotline: '0981 123 457', phone: '0981 123 457' }
];

interface ServiceCategory {
  id?: number;
  category_id?: number;
  name: string;
  estimate_time?: number;
}

interface PatientForm {
  fullName: string;
  phone: string;
  email: string;
  dob: string;
  category_id: number | '';
  start_time: string;
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

export default function BookingForm() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const userId = searchParams?.get('user_id');

  // UI State
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(true);
  const [honeypot, setHoneypot] = useState('');

  // Data State
  const [clinics, setClinics] = useState<Clinic[]>(DEFAULT_CLINICS);
  const [categories, setCategories] = useState<ServiceCategory[]>([]);
  
  // Form State
  const [selectedClinic, setSelectedClinic] = useState<number | string | null>(1);
  const [selectedDoctor, setSelectedDoctor] = useState<number | string>(1);
  const [patients, setPatients] = useState<PatientForm[]>([
    { fullName: '', phone: '', email: '', dob: '', category_id: '', start_time: '' }
  ]);
  const [selectedDate, setSelectedDate] = useState<string>('');
  const [selectedTime, setSelectedTime] = useState<string>('');

  // Result State
  const [matrixData, setMatrixData] = useState<MatrixRow[]>([]);
  const [bookingSuccess, setBookingSuccess] = useState(false);
  const [groupCode, setGroupCode] = useState<string>('');
  const [myBookingIds, setMyBookingIds] = useState<number[]>([]);

  // --- INITIAL FETCH ---
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clinicRes, categoryRes] = await Promise.all([
          fetch('/api/clinics/'),
          fetch('/api/services/')
        ]);
        if (clinicRes.ok) {
          const clinicData = await clinicRes.json();
          if (Array.isArray(clinicData) && clinicData.length > 0) setClinics(clinicData);
        }
        if (categoryRes.ok) {
          const categoryData = await categoryRes.json();
          if (Array.isArray(categoryData) && categoryData.length > 0) setCategories(categoryData);
        }
      } catch (error) {
        console.error("Lỗi khi tải dữ liệu API:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
    setSelectedDate(new Date().toISOString().split('T')[0]);
  }, []);

  // --- MATRIX LOGIC ---
  const fetchMatrix = () => {
    if (selectedClinic && selectedDate) {
      axios.get(`/api/daily-schedule/?clinic_id=${selectedClinic}&date=${selectedDate}&t=${new Date().getTime()}`)
        .then(res => setMatrixData(res.data))
        .catch(err => console.error(err));
    }
  };

  useEffect(() => {
    fetchMatrix();
  }, [selectedClinic, selectedDate]);

  const maxChairs = matrixData.length > 0 ? matrixData[0].chairs.length : 0;

  const validStartTimes = useMemo(() => {
    if (matrixData.length === 0 || patients.length === 0) return new Set();
    const valid = new Set<string>();

    for (let i = 0; i < matrixData.length; i++) {
      let allPatientsSatisfied = true;
      const occupiedChairs = new Set<number>();

      for (let p of patients) {
        const s = categories.find(srv => (srv.category_id || srv.id) === p.category_id);
        const duration = s?.estimate_time || 30;
        const slotsNeeded = Math.ceil(duration / 30);

        let foundChair = false;
        for (let chairNum = 1; chairNum <= maxChairs; chairNum++) {
          if (occupiedChairs.has(chairNum)) continue;

          let isAvailable = true;
          for (let step = 0; step < slotsNeeded; step++) {
            if (i + step >= matrixData.length) { isAvailable = false; break; }
            const cell = matrixData[i + step].chairs.find(c => c.chair === chairNum);
            if (!cell || cell.status !== 'available') { isAvailable = false; break; }
          }
          if (isAvailable) {
            foundChair = true;
            occupiedChairs.add(chairNum);
            break;
          }
        }
        if (!foundChair) { allPatientsSatisfied = false; break; }
      }
      if (allPatientsSatisfied) valid.add(matrixData[i].start_time);
    }
    return valid;
  }, [matrixData, patients, categories, maxChairs]);

  const previewAssignments = useMemo(() => {
    if (bookingSuccess || !selectedTime) return [];
    const assignments: any[] = [];
    const startIndex = matrixData.findIndex(r => r.start_time === selectedTime);
    if (startIndex === -1) return [];

    const occupiedChairs = new Set();
    for (let i = 0; i < patients.length; i++) {
      const p = patients[i];
      const s = categories.find(srv => (srv.category_id || srv.id) === p.category_id);
      const duration = s?.estimate_time || 30;
      const slotsNeeded = Math.ceil(duration / 30);

      let assignedChair = null;
      for (let chairNum = 1; chairNum <= maxChairs; chairNum++) {
        if (occupiedChairs.has(chairNum)) continue;
        let isAvailable = true;
        for (let step = 0; step < slotsNeeded; step++) {
          if (startIndex + step >= matrixData.length) { isAvailable = false; break; }
          const cell = matrixData[startIndex + step].chairs.find(c => c.chair === chairNum);
          if (!cell || cell.status !== 'available') { isAvailable = false; break; }
        }
        if (isAvailable) { assignedChair = chairNum; break; }
      }
      if (assignedChair) {
        occupiedChairs.add(assignedChair);
        assignments.push({
          chair: assignedChair,
          startIndex: startIndex,
          slotsNeeded: slotsNeeded,
          patientName: p.fullName || `Khách ${i+1}`,
          serviceName: s ? s.name : ''
        });
      }
    }
    return assignments;
  }, [selectedTime, patients, categories, matrixData, bookingSuccess, maxChairs]);

  // --- ACTIONS ---
  const addPatient = () => {
    setPatients([...patients, { fullName: '', phone: '', email: '', dob: '', category_id: '', start_time: '' }]);
  };

  const removePatient = (index: number) => {
    if (patients.length > 1) {
      const updated = patients.filter((_, i) => i !== index);
      setPatients(updated);
    }
  };

  const handlePatientChange = (index: number, field: keyof PatientForm, value: string | number) => {
    const updated = [...patients];
    updated[index] = { ...updated[index], [field]: value };
    setPatients(updated);
  };

  const handleBookingSubmit = async () => {
    if (honeypot) return;
    if (!selectedClinic || !selectedDate || !selectedTime) {
      alert("Vui lòng chọn đầy đủ Khung giờ trước khi hoàn tất!");
      return;
    }

    const isValid = patients.every(p => p.fullName.trim() !== '' && p.phone.trim() !== '' && p.category_id !== '');
    if (!isValid) {
      alert("Vui lòng điền đủ Họ tên, SĐT và chọn Dịch vụ cho tất cả các khách hàng!");
      return;
    }

    const isValidPhone = patients.every(p => p.phone.length >= 10 && p.phone.length <= 11);
    if (!isValidPhone) {
      alert("Số điện thoại không hợp lệ! Vui lòng nhập từ 10 đến 11 chữ số.");
      return;
    }

    try {
      const payload = {
        clinic_id: selectedClinic,
        date: selectedDate,
        start_time: selectedTime,
        created_user_id: userId ? parseInt(userId) : null,
        patients: patients.map(p => ({
          fullName: p.fullName,
          phone: p.phone,
          email: p.email,
          dob: p.dob ? `${p.dob}-01-01` : "",
          category_id: p.category_id,
          start_time: p.start_time || selectedTime
        }))
      };

      const response = await fetch('/api/bookings/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) {
        const data = await response.json();
        setGroupCode(data.group_code || "N/A");
        setMyBookingIds(data.created_booking_ids || []);
        setBookingSuccess(true);
        // Scroll to top to see success message
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        const errText = await response.text();
        alert("Lỗi đặt lịch: " + errText);
      }
    } catch (error) {
      console.error(error);
      alert("Có lỗi xảy ra khi kết nối máy chủ.");
    }
  };

  const resetForm = () => {
    setPatients([{ fullName: '', phone: '', email: '', dob: '', category_id: '', start_time: '' }]);
    setSelectedTime('');
    setBookingSuccess(false);
    setGroupCode('');
    setMyBookingIds([]);
    setCurrentStep(1);
  };

  // --- RENDER SUCCESS ---
  if (bookingSuccess) {
    return (
      <main className="min-h-screen bg-gray-50 flex flex-col items-center p-4 md:p-8">
        <div className="w-full max-w-3xl bg-white rounded-3xl shadow-xl p-8 text-center animate-fade-in">
          <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-6">
            <svg className="w-12 h-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Đặt Lịch Khám Thành Công!</h1>
          <p className="text-gray-500 mb-6">Cảm ơn bạn đã tin tưởng dịch vụ của chúng tôi.</p>
          
          <div className="inline-block bg-blue-50 border border-blue-200 rounded-2xl px-6 py-4 mb-8">
            <span className="text-sm text-blue-600 font-semibold uppercase tracking-wider block mb-1">Mã nhóm đặt lịch</span>
            <span className="text-3xl font-mono font-bold text-blue-800 tracking-widest">{groupCode}</span>
          </div>

          <div className="text-left border-t border-gray-100 pt-8 mb-8">
            <h3 className="font-bold text-gray-800 mb-4 flex items-center">
              <svg className="w-5 h-5 mr-2 text-blue-500" fill="currentColor" viewBox="0 0 20 20"><path d="M9 6a3 3 0 11-6 0 3 3 0 016 0zM17 6a3 3 0 11-6 0 3 3 0 016 0zM12.93 17c.046-.327.07-.66.07-1a6.97 6.97 0 00-1.5-4.33A5 5 0 0119 16v1h-6.07zM6 11a7 7 0 00-7 7v1h12v-1a7 7 0 00-7-7z" /></svg>
              Danh sách người khám ({patients.length})
            </h3>
            <div className="overflow-hidden rounded-xl border border-gray-100">
              <table className="w-full text-sm">
                <thead className="bg-gray-50 text-gray-600">
                  <tr>
                    <th className="px-4 py-3 text-left">Họ tên</th>
                    <th className="px-4 py-3 text-left">Dịch vụ</th>
                    <th className="px-4 py-3 text-center">Giờ khám</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {patients.map((p, idx) => (
                    <tr key={idx}>
                      <td className="px-4 py-3 font-medium">{p.fullName}</td>
                      <td className="px-4 py-3 text-gray-500">
                        {categories.find(c => (c.category_id || c.id) === p.category_id)?.name || 'Khám tổng quát'}
                      </td>
                      <td className="px-4 py-3 text-center font-semibold text-blue-600">{p.start_time || selectedTime}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 p-4 bg-gray-50 rounded-xl text-sm text-gray-600">
              <p><strong>Cơ sở:</strong> {clinics.find(c => (c.clinic_id || c.id) === selectedClinic)?.name}</p>
              <p><strong>Ngày khám:</strong> {selectedDate}</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={resetForm}
              className="px-8 py-3 bg-white border-2 border-blue-600 text-blue-600 font-bold rounded-xl hover:bg-blue-50 transition-all"
            >
              Đặt thêm lịch mới
            </button>
            <button 
              onClick={() => router.push(`/booking/success/${myBookingIds[0] || groupCode}`)}
              className="px-8 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 shadow-lg shadow-blue-200 transition-all"
            >
              Xem chi tiết biên nhận
            </button>
          </div>
        </div>
      </main>
    );
  }

  // --- RENDER MAIN FORM ---
  return (
    <main className="min-h-screen bg-gray-50 flex flex-col items-center p-4 md:p-8">
      <div className="w-full max-w-6xl">
        <h1 className="text-3xl font-bold text-center text-blue-700 mb-10">Đặt Lịch Khám Nha Khoa</h1>

        {/* STEP INDICATOR */}
        <div className="flex items-center justify-center mb-10 space-x-4">
          {[1, 2, 3].map(step => (
            <div key={step} className="flex items-center">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all ${currentStep >= step ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-500'}`}>
                {step}
              </div>
              {step < 3 && <div className={`w-12 h-1 mb-0 mx-2 rounded ${currentStep > step ? 'bg-blue-600' : 'bg-gray-200'}`} />}
            </div>
          ))}
        </div>
        
        {/* STEP 1: CLINIC */}
        {currentStep === 1 && (
          <div className="animate-fade-in">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Bước 1: Lựa chọn cơ sở khám</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
              {clinics.map((clinic) => {
                const safeId = clinic.clinic_id || clinic.id;
                return (
                  <button 
                    key={safeId}
                    onClick={() => setSelectedClinic(safeId!)}
                    className={`text-left p-6 border-2 rounded-2xl transition-all ${
                      selectedClinic === safeId 
                        ? 'border-blue-500 bg-blue-50 shadow-md ring-2 ring-blue-200' 
                        : 'border-white bg-white hover:border-blue-200 shadow-sm'
                    }`}
                  >
                    <h3 className="font-bold text-lg text-gray-800 mb-1">{clinic.name}</h3>
                    <p className="text-gray-500 text-sm mb-3">{clinic.address}</p>
                    <div className="flex items-center text-blue-600 text-sm font-medium">
                      <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" /></svg>
                      {clinic.hotline || clinic.phone}
                    </div>
                  </button>
                );
              })}
            </div>

            {selectedClinic && (
              <div className="bg-white rounded-2xl p-4 shadow-sm border border-gray-100 mb-8 h-80">
                <iframe 
                  width="100%" height="100%" frameBorder="0" className="rounded-xl"
                  src={`https://maps.google.com/maps?q=${encodeURIComponent(clinics.find(c => (c.clinic_id || c.id) === selectedClinic)?.address || '')}&t=&z=16&ie=UTF8&iwloc=&output=embed`}
                />
              </div>
            )}

            <div className="flex justify-end">
              <button 
                onClick={() => setCurrentStep(2)}
                className="px-10 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-100"
              >
                Tiếp tục
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: PATIENTS */}
        {currentStep === 2 && (
          <div className="animate-fade-in">
            <div className="flex flex-col md:flex-row md:items-center justify-between mb-6 gap-4">
              <h2 className="text-xl font-semibold text-gray-800">Bước 2: Thông tin người khám ({patients.length})</h2>
              <button 
                onClick={addPatient}
                className="flex items-center justify-center px-4 py-2 bg-green-50 text-green-700 border border-green-200 font-bold rounded-lg hover:bg-green-100 transition-all"
              >
                <svg className="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" /></svg>
                Thêm người đi cùng
              </button>
            </div>

            {/* DOCTOR SELECTION (HIDDEN BY FLAG) */}
            {SHOW_DOCTOR_SELECTION && (
              <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-8">
                <h3 className="font-bold text-gray-800 mb-4">Chọn bác sĩ mong muốn</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {DOCTORS.map(doc => (
                    <div 
                      key={doc.id}
                      onClick={() => setSelectedDoctor(doc.id)}
                      className={`p-4 border-2 rounded-xl cursor-pointer transition-all ${selectedDoctor === doc.id ? 'border-blue-500 bg-blue-50' : 'border-gray-100 hover:border-blue-200'}`}
                    >
                      <p className="font-bold text-gray-800">{doc.name}</p>
                      <p className="text-xs text-gray-500">{doc.title}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="space-y-6 mb-8">
              {patients.map((p, index) => (
                <div key={index} className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 relative group">
                  <div className="absolute -top-3 -left-3 bg-blue-600 text-white w-8 h-8 flex items-center justify-center rounded-full font-bold shadow-md z-10">
                    {index + 1}
                  </div>
                  
                  {index > 0 && (
                    <button 
                      onClick={() => removePatient(index)}
                      className="absolute top-4 right-4 text-gray-400 hover:text-red-500 transition-colors"
                      title="Xóa người này"
                    >
                      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
                    </button>
                  )}

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <div className="md:col-span-1">
                      <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Họ và tên *</label>
                      <input 
                        type="text" value={p.fullName} 
                        onChange={(e) => handlePatientChange(index, 'fullName', e.target.value)}
                        className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 outline-none transition-all"
                        placeholder="Nguyễn Văn A"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Số điện thoại *</label>
                      <input 
                        type="text" value={p.phone} 
                        onChange={(e) => handlePatientChange(index, 'phone', e.target.value.replace(/\D/g, '').slice(0, 11))}
                        className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 outline-none transition-all"
                        placeholder="09xxxxxxxx"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Email</label>
                      <input 
                        type="email" value={p.email} 
                        onChange={(e) => handlePatientChange(index, 'email', e.target.value)}
                        className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 outline-none transition-all"
                        placeholder="example@gmail.com"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Năm sinh</label>
                      <input 
                        type="number" value={p.dob} 
                        onChange={(e) => handlePatientChange(index, 'dob', e.target.value)}
                        className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 outline-none transition-all"
                        placeholder="VD: 1995"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Dịch vụ cần khám *</label>
                      <select 
                        value={p.category_id} 
                        onChange={(e) => handlePatientChange(index, 'category_id', parseInt(e.target.value) || '')}
                        className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 outline-none transition-all"
                      >
                        <option value="">-- Chọn dịch vụ --</option>
                        {categories.map(cat => (
                          <option key={cat.category_id || cat.id} value={cat.category_id || cat.id}>
                            {cat.name} {cat.estimate_time ? `(~${cat.estimate_time}p)` : ''}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-bold text-gray-500 uppercase mb-1">Giờ khám riêng (Tùy chọn)</label>
                      <select 
                        value={p.start_time} 
                        onChange={(e) => handlePatientChange(index, 'start_time', e.target.value)}
                        className="w-full px-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:bg-white focus:border-blue-500 outline-none transition-all"
                      >
                        <option value="">Theo giờ chung của nhóm</option>
                        {TIME_SLOTS.map(slot => <option key={slot} value={slot}>{slot}</option>)}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="flex justify-between">
              <button 
                onClick={() => setCurrentStep(1)}
                className="px-8 py-3 bg-gray-200 text-gray-700 font-bold rounded-xl hover:bg-gray-300 transition-all"
              >
                Quay lại
              </button>
              <button 
                onClick={() => setCurrentStep(3)}
                className="px-10 py-3 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-all shadow-lg shadow-blue-100"
              >
                Tiếp tục
              </button>
            </div>
          </div>
        )}

        {/* STEP 3: DATE & TIME MATRIX */}
        {currentStep === 3 && (
          <div className="animate-fade-in">
            <h2 className="text-xl font-semibold text-gray-800 mb-6">Bước 3: Chọn ngày và khung giờ khám</h2>
            
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-gray-100 mb-8">
              <div className="max-w-xs mb-8">
                <label className="block text-sm font-bold text-gray-700 mb-2">Ngày khám</label>
                <input 
                  type="date" 
                  value={selectedDate}
                  min={new Date().toISOString().split('T')[0]}
                  onChange={(e) => { setSelectedDate(e.target.value); setSelectedTime(''); }}
                  className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:border-blue-500 outline-none"
                />
              </div>

              <div className="mb-4 flex flex-wrap gap-4 text-xs font-bold uppercase tracking-wider">
                <div className="flex items-center"><div className="w-4 h-4 bg-green-50 border border-green-200 rounded mr-2"></div> Trống</div>
                <div className="flex items-center"><div className="w-4 h-4 bg-gray-100 border border-gray-200 rounded mr-2"></div> Đã đặt</div>
                <div className="flex items-center"><div className="w-4 h-4 bg-blue-200 border-2 border-blue-400 rounded mr-2"></div> Đang chọn</div>
              </div>

              <div className="overflow-x-auto rounded-xl border border-gray-200">
                <div className="min-w-[800px]">
                  {/* Header */}
                  <div className="flex bg-gray-50 border-b border-gray-200 sticky top-0 z-10">
                    <div className="w-28 shrink-0 p-4 font-bold text-gray-600 text-center border-r border-gray-200">Giờ</div>
                    {Array.from({ length: maxChairs }).map((_, i) => (
                      <div key={i} className="flex-1 p-4 font-bold text-gray-600 text-center border-r border-gray-200 last:border-0">
                        Ghế {i + 1}
                      </div>
                    ))}
                  </div>

                  {/* Rows */}
                  <div className="max-h-[500px] overflow-y-auto">
                    {matrixData.map((row, rowIndex) => {
                      const isValidStart = validStartTimes.has(row.start_time);
                      const isRowSelected = selectedTime === row.start_time;

                      return (
                        <div 
                          key={row.start_time} 
                          className={`flex h-20 group transition-colors ${isValidStart ? 'cursor-pointer' : ''}`}
                          onClick={() => isValidStart && setSelectedTime(row.start_time)}
                        >
                          <div className={`w-28 shrink-0 flex items-center justify-center font-bold border-r border-b border-gray-100 ${isRowSelected ? 'bg-blue-600 text-white' : 'bg-white text-gray-500 group-hover:bg-blue-50'}`}>
                            {row.start_time}
                          </div>
                          
                          {row.chairs.map((c) => {
                            let cellContent = null;
                            let bgClass = "bg-white";
                            let isFirst = true;
                            let mergeDown = false;

                            // Check Booked
                            if (c.booking_id) {
                              bgClass = "bg-gray-100 text-gray-400";
                              const prevRow = matrixData[rowIndex - 1];
                              if (prevRow && prevRow.chairs.find(x => x.chair === c.chair)?.booking_id === c.booking_id) isFirst = false;
                              const nextRow = matrixData[rowIndex + 1];
                              if (nextRow && nextRow.chairs.find(x => x.chair === c.chair)?.booking_id === c.booking_id) mergeDown = true;

                              if (isFirst) {
                                cellContent = <div className="text-[10px] leading-tight font-medium px-1 truncate w-full">Đã đặt</div>;
                              }
                            } else {
                              // Check Preview
                              const assignment = previewAssignments.find(a => a.chair === c.chair);
                              if (assignment && rowIndex >= assignment.startIndex && rowIndex < assignment.startIndex + assignment.slotsNeeded) {
                                bgClass = "bg-blue-200 text-blue-800 border-x-2 border-blue-400";
                                if (rowIndex === assignment.startIndex) {
                                  isFirst = true;
                                  bgClass += " border-t-2 rounded-t-lg";
                                  cellContent = (
                                    <div className="text-[10px] font-bold truncate w-full px-1">
                                      {assignment.patientName}
                                    </div>
                                  );
                                } else {
                                  isFirst = false;
                                }
                                if (rowIndex === assignment.startIndex + assignment.slotsNeeded - 1) {
                                  bgClass += " border-b-2 rounded-b-lg";
                                } else {
                                  mergeDown = true;
                                }
                              } else {
                                bgClass = "bg-green-50/30 group-hover:bg-blue-50/30";
                              }
                            }

                            return (
                              <div key={c.chair} className={`flex-1 border-r border-b border-gray-100 p-1 flex items-center justify-center text-center transition-all ${bgClass}`}>
                                {cellContent}
                              </div>
                            );
                          })}
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-between items-center">
              <button 
                onClick={() => setCurrentStep(2)}
                className="px-8 py-3 bg-gray-200 text-gray-700 font-bold rounded-xl hover:bg-gray-300 transition-all"
              >
                Quay lại
              </button>
              
              <div className="flex items-center gap-4">
                <input type="text" className="hidden" value={honeypot} onChange={(e) => setHoneypot(e.target.value)} tabIndex={-1} />
                <button 
                  onClick={handleBookingSubmit}
                  disabled={!selectedTime}
                  className={`px-12 py-4 font-bold text-lg rounded-xl shadow-lg transition-all ${
                    selectedTime 
                      ? 'bg-green-600 text-white hover:bg-green-700 hover:-translate-y-1' 
                      : 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  }`}
                >
                  Xác nhận Đặt lịch
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      <style jsx global>{`
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in {
          animation: fadeIn 0.4s ease-out forwards;
        }
      `}</style>
    </main>
  );
}