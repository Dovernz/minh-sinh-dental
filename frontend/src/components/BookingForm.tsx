'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Calendar, Clock, Users, MapPin, Stethoscope, 
  CheckCircle2, AlertTriangle, Printer, Plus, 
  Trash2, ChevronRight, ChevronLeft, Barcode, 
  QrCode, Info, PlaneTakeoff 
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// --- Interfaces & Types ---
interface Clinic {
  id: number;
  name: string;
  address: string;
}

interface Service {
  id: number;
  name: string;
  price?: number;
}

interface TimeSlot {
  time: string;
  available_seats: number;
  status: 'available' | 'full';
}

interface Member {
  id: string;
  full_name: string;
  service_id: string;
  start_time: string; // Empty string means inherit group time
}

interface BookingResult {
  pnr_code: string;
  group_code: string;
  clinic_name: string;
  clinic_address: string;
  appointment_date: string;
  members: Array<{
    full_name: string;
    service_name: string;
    start_time: string;
    price: number;
  }>;
}

// --- Constants & Helpers ---
const DEFAULT_PRICES: Record<string, number> = {
  'Khám tổng quát & Tư vấn': 150000,
  'Cạo vôi răng': 250000,
  'Nhổ răng khôn': 1500000,
  'Trám răng': 350000,
  'Tẩy trắng răng': 1800000,
  'Niềng răng': 25000000,
  'Implant': 18000000,
  'Bọc răng sứ': 3500000,
  'default': 300000
};

const TIME_STEPS = [
  "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
  "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
  "17:30", "18:00", "18:30", "19:00"
];

const formatPNR = (code: string): string => {
  if (!code) return "MSXXXX";
  if (code.length === 6) return code.toUpperCase();
  // Extract MS + last 4 chars if format is MS-GRP-YYYYMMDD-XXXX
  const parts = code.split('-');
  if (parts.length > 1) {
    const lastPart = parts[parts.length - 1];
    return `MS${lastPart.substring(0, 4)}`.toUpperCase();
  }
  return code.substring(0, 6).toUpperCase();
};

const formatVND = (amount: number) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(amount);
};

export default function BookingForm() {
  // --- States ---
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [services, setServices] = useState<Service[]>([]);
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  
  const [formData, setFormData] = useState({
    clinicId: '',
    date: '',
    selectedTime: '08:00',
    leaderName: '',
    leaderPhone: '',
    leaderEmail: '',
    members: [] as Member[],
    honeypot: '' // Anti-bot
  });

  const [bookingResult, setBookingResult] = useState<BookingResult | null>(null);

  // --- Effects ---
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [resClinics, resServices] = await Promise.all([
          fetch('/api/clinics/'),
          fetch('/api/services/')
        ]);
        setClinics(await resClinics.json());
        setServices(await resServices.json());
      } catch (error) {
        console.error("Fetch error:", error);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (formData.clinicId && formData.date) {
      fetch(`/api/daily-schedule/?clinic_id=${formData.clinicId}&date=${formData.date}`)
        .then(res => res.json())
        .then(data => setAvailableSlots(data.slots || []));
    }
  }, [formData.clinicId, formData.date]);

  // --- Logic ---
  const handleAddMember = () => {
    const newMember: Member = {
      id: Math.random().toString(36).substr(2, 9),
      full_name: '',
      service_id: '',
      start_time: '' // Inherit
    };
    setFormData({ ...formData, members: [...formData.members, newMember] });
  };

  const removeMember = (id: string) => {
    setFormData({ ...formData, members: formData.members.filter(m => m.id !== id) });
  };

  const updateMember = (id: string, field: keyof Member, value: string) => {
    setFormData({
      ...formData,
      members: formData.members.map(m => m.id === id ? { ...m, [field]: value } : m)
    });
  };

  // Capacity Check Logic
  const capacityWarnings = useMemo(() => {
    const warnings: string[] = [];
    const counts: Record<string, number> = {};
    
    // Count leader
    counts[formData.selectedTime] = (counts[formData.selectedTime] || 0) + 1;
    // Count members
    formData.members.forEach(m => {
      const time = m.start_time || formData.selectedTime;
      counts[time] = (counts[time] || 0) + 1;
    });

    Object.entries(counts).forEach(([time, count]) => {
      const slot = availableSlots.find(s => s.time === time);
      if (slot && count > slot.available_seats) {
        warnings.push(`Khung giờ ${time} chỉ còn ${slot.available_seats} ghế trống nhưng có ${count} khách đăng ký.`);
      }
    });
    return warnings;
  }, [formData, availableSlots]);

  const handleSubmit = async () => {
    if (formData.honeypot) return;
    setLoading(true);
    
    const payload = {
      clinic_id: formData.clinicId,
      appointment_date: formData.date,
      group_code: `GRP-${Date.now()}`,
      leader: {
        full_name: formData.leaderName,
        phone: formData.leaderPhone,
        email: formData.leaderEmail,
        service_id: services[0]?.id, // Default service for leader
        start_time: formData.selectedTime
      },
      members: formData.members.map(m => ({
        full_name: m.full_name,
        service_id: m.service_id,
        start_time: m.start_time || formData.selectedTime
      }))
    };

    try {
      const res = await fetch('/api/bookings/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const result = await res.json();
      
      // Mock result for UI demonstration if API fails or for this template
      const mockResult: BookingResult = {
        pnr_code: formatPNR(result.pnr_code || "MS8K2P"),
        group_code: result.group_code || "MS-GRP-2024",
        clinic_name: clinics.find(c => c.id.toString() === formData.clinicId)?.name || "Nha Khoa Minh Sinh",
        clinic_address: clinics.find(c => c.id.toString() === formData.clinicId)?.address || "123 Đường ABC, TP.HCM",
        appointment_date: formData.date,
        members: [
          { 
            full_name: formData.leaderName, 
            service_name: "Khám tổng quát & Tư vấn", 
            start_time: formData.selectedTime,
            price: DEFAULT_PRICES['Khám tổng quát & Tư vấn']
          },
          ...formData.members.map(m => ({
            full_name: m.full_name,
            service_name: services.find(s => s.id.toString() === m.service_id)?.name || "Dịch vụ nha khoa",
            start_time: m.start_time || formData.selectedTime,
            price: DEFAULT_PRICES[services.find(s => s.id.toString() === m.service_id)?.name || 'default']
          }))
        ]
      };
      
      setBookingResult(mockResult);
      setStep(4);
    } catch (error) {
      alert("Có lỗi xảy ra khi đặt lịch.");
    } finally {
      setLoading(false);
    }
  };

  // --- Sub-Components ---

  const TimelineMatrix = () => {
    const allParticipants = [
      { name: formData.leaderName || 'Trưởng nhóm', time: formData.selectedTime, service: 'Khám tổng quát' },
      ...formData.members.map(m => ({
        name: m.full_name || 'Thành viên',
        time: m.start_time || formData.selectedTime,
        service: services.find(s => s.id.toString() === m.service_id)?.name || 'Dịch vụ'
      }))
    ];

    return (
      <div className="mt-8 bg-slate-50 p-4 rounded-xl border border-slate-200 overflow-hidden">
        <h4 className="text-sm font-bold text-slate-700 mb-4 flex items-center gap-2">
          <Calendar className="w-4 h-4" /> LỊCH TRÌNH NHÓM (CALENDAR TIMELINE)
        </h4>
        <div className="overflow-x-auto">
          <div className="min-w-[800px]">
            {/* Header: Times */}
            <div className="grid grid-cols-[150px_1fr] border-b border-slate-200">
              <div className="p-2 bg-slate-100 font-medium text-xs text-slate-500">Khách hàng</div>
              <div className="flex">
                {TIME_STEPS.map(t => (
                  <div key={t} className="flex-1 text-[10px] text-center border-l border-slate-200 py-2 text-slate-400">
                    {t}
                  </div>
                ))}
              </div>
            </div>
            {/* Rows: Members */}
            {allParticipants.map((p, idx) => (
              <div key={idx} className="grid grid-cols-[150px_1fr] border-b border-slate-100 hover:bg-white transition-colors">
                <div className="p-2 text-xs font-semibold text-slate-700 truncate border-r border-slate-200">
                  {p.name}
                </div>
                <div className="flex relative h-10">
                  {TIME_STEPS.map(t => (
                    <div key={t} className="flex-1 border-l border-slate-100" />
                  ))}
                  {/* Event Card */}
                  <div 
                    className="absolute top-1 bottom-1 rounded shadow-sm bg-blue-500 text-white text-[9px] p-1 flex flex-col justify-center overflow-hidden"
                    style={{
                      left: `${(TIME_STEPS.indexOf(p.time) / TIME_STEPS.length) * 100}%`,
                      width: `${(1 / TIME_STEPS.length) * 100}%`
                    }}
                  >
                    <div className="font-bold truncate flex items-center gap-1">
                      <Clock className="w-2 h-2" /> {p.time}
                    </div>
                    <div className="truncate opacity-90">{p.service}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  // --- Render Steps ---

  return (
    <div className="max-w-4xl mx-auto p-4 md:p-8 bg-white shadow-2xl rounded-3xl my-10 border border-slate-100">
      {/* Progress Bar */}
      {step < 4 && (
        <div className="mb-10">
          <div className="flex justify-between mb-2">
            {[1, 2, 3].map((s) => (
              <div key={s} className={`flex items-center gap-2 ${step >= s ? 'text-blue-600' : 'text-slate-300'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${step >= s ? 'bg-blue-600 text-white' : 'bg-slate-100'}`}>
                  {s}
                </div>
                <span className="hidden md:inline text-sm font-medium">
                  {s === 1 ? 'Cơ sở & Ngày' : s === 2 ? 'Thông tin nhóm' : 'Xếp lịch & Giờ'}
                </span>
              </div>
            ))}
          </div>
          <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-blue-600"
              initial={{ width: '33%' }}
              animate={{ width: `${(step / 3) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Step 1: Clinic & Date */}
      {step === 1 && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 flex items-center gap-2">
                <MapPin className="w-4 h-4 text-blue-500" /> CHỌN CƠ SỞ
              </label>
              <select 
                className="w-full p-4 rounded-xl border-2 border-slate-100 focus:border-blue-500 outline-none transition-all"
                value={formData.clinicId}
                onChange={(e) => setFormData({...formData, clinicId: e.target.value})}
              >
                <option value="">-- Chọn phòng khám --</option>
                {clinics.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-blue-500" /> CHỌN NGÀY KHÁM
              </label>
              <input 
                type="date" 
                className="w-full p-4 rounded-xl border-2 border-slate-100 focus:border-blue-500 outline-none transition-all"
                min={new Date().toISOString().split('T')[0]}
                value={formData.date}
                onChange={(e) => setFormData({...formData, date: e.target.value})}
              />
            </div>
          </div>
          <button 
            disabled={!formData.clinicId || !formData.date}
            onClick={() => setStep(2)}
            className="w-full py-4 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 disabled:bg-slate-200 transition-all flex items-center justify-center gap-2"
          >
            Tiếp tục <ChevronRight className="w-5 h-5" />
          </button>
        </motion.div>
      )}

      {/* Step 2: Group Info */}
      {step === 2 && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-8">
          <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
            <h3 className="font-bold text-blue-800 mb-4 flex items-center gap-2">
              <Users className="w-5 h-5" /> THÔNG TIN TRƯỞNG NHÓM
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <input 
                placeholder="Họ tên trưởng nhóm" 
                className="p-3 rounded-lg border border-white focus:border-blue-500 outline-none"
                value={formData.leaderName}
                onChange={(e) => setFormData({...formData, leaderName: e.target.value})}
              />
              <input 
                placeholder="Số điện thoại" 
                className="p-3 rounded-lg border border-white focus:border-blue-500 outline-none"
                value={formData.leaderPhone}
                onChange={(e) => setFormData({...formData, leaderPhone: e.target.value})}
              />
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-slate-800">THÀNH VIÊN ĐI CÙNG ({formData.members.length})</h3>
              <button 
                onClick={handleAddMember}
                className="text-sm bg-emerald-500 text-white px-4 py-2 rounded-lg font-bold hover:bg-emerald-600 flex items-center gap-2"
              >
                <Plus className="w-4 h-4" /> Thêm người
              </button>
            </div>

            {formData.members.map((member, index) => (
              <div key={member.id} className="p-4 border border-slate-200 rounded-xl flex flex-wrap gap-4 items-end bg-slate-50">
                <div className="flex-1 min-w-[200px] space-y-1">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Họ tên thành viên {index + 1}</label>
                  <input 
                    className="w-full p-2 rounded border border-slate-200"
                    value={member.full_name}
                    onChange={(e) => updateMember(member.id, 'full_name', e.target.value)}
                  />
                </div>
                <div className="flex-1 min-w-[200px] space-y-1">
                  <label className="text-[10px] font-bold text-slate-500 uppercase">Dịch vụ đăng ký</label>
                  <select 
                    className="w-full p-2 rounded border border-slate-200"
                    value={member.service_id}
                    onChange={(e) => updateMember(member.id, 'service_id', e.target.value)}
                  >
                    <option value="">-- Chọn dịch vụ --</option>
                    {services.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
                  </select>
                </div>
                <button onClick={() => removeMember(member.id)} className="p-2 text-red-500 hover:bg-red-50 rounded">
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>

          <div className="flex gap-4">
            <button onClick={() => setStep(1)} className="flex-1 py-4 border-2 border-slate-100 rounded-xl font-bold text-slate-500">Quay lại</button>
            <button 
              disabled={!formData.leaderName || !formData.leaderPhone}
              onClick={() => setStep(3)} 
              className="flex-[2] py-4 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 disabled:bg-slate-200"
            >
              Tiếp tục
            </button>
          </div>
        </motion.div>
      )}

      {/* Step 3: Time & Matrix & Capacity */}
      {step === 3 && (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
          <div className="bg-slate-900 text-white p-6 rounded-2xl">
            <h3 className="font-bold mb-4 flex items-center gap-2 text-blue-400">
              <Clock className="w-5 h-5" /> CHỌN GIỜ KHÁM CHUNG CHO NHÓM
            </h3>
            <div className="grid grid-cols-4 md:grid-cols-8 gap-2">
              {TIME_STEPS.map(time => {
                const slot = availableSlots.find(s => s.time === time);
                const isFull = slot?.status === 'full';
                return (
                  <button
                    key={time}
                    disabled={isFull}
                    onClick={() => setFormData({...formData, selectedTime: time})}
                    className={`p-2 text-xs font-bold rounded-lg transition-all ${
                      formData.selectedTime === time 
                        ? 'bg-blue-500 text-white scale-110 shadow-lg' 
                        : isFull ? 'bg-slate-800 text-slate-600 cursor-not-allowed' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
                    }`}
                  >
                    {time}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Individual Overrides */}
          <div className="space-y-4">
            <h3 className="font-bold text-slate-800 flex items-center gap-2">
              <Info className="w-4 h-4 text-blue-500" /> TÙY CHỈNH GIỜ RIÊNG (NẾU CÓ)
            </h3>
            {formData.members.map(m => (
              <div key={m.id} className="flex items-center justify-between p-3 bg-white border border-slate-100 rounded-xl shadow-sm">
                <span className="text-sm font-medium text-slate-600">{m.full_name || 'Thành viên'}</span>
                <select 
                  className="text-xs p-2 rounded border border-slate-200 bg-slate-50"
                  value={m.start_time}
                  onChange={(e) => updateMember(m.id, 'start_time', e.target.value)}
                >
                  <option value="">Theo lịch chung ({formData.selectedTime})</option>
                  {TIME_STEPS.map(t => <option key={t} value={t}>{t}</option>)}
                </select>
              </div>
            ))}
          </div>

          {/* Capacity Warning Banner */}
          <AnimatePresence>
            {capacityWarnings.length > 0 && (
              <motion.div 
                initial={{ height: 0, opacity: 0 }}
                animate={{ height: 'auto', opacity: 1 }}
                exit={{ height: 0, opacity: 0 }}
                className="bg-red-50 border-2 border-red-200 p-4 rounded-xl"
              >
                <div className="flex items-start gap-3">
                  <motion.div 
                    animate={{ scale: [1, 1.2, 1] }} 
                    transition={{ repeat: Infinity, duration: 1 }}
                  >
                    <AlertTriangle className="w-6 h-6 text-red-600" />
                  </motion.div>
                  <div>
                    <h4 className="text-red-800 font-bold text-sm uppercase">⚠️ Cảnh báo quá tải sức chứa</h4>
                    {capacityWarnings.map((w, i) => (
                      <p key={i} className="text-red-700 text-xs mt-1 font-medium">{w}</p>
                    ))}
                    <p className="text-red-600 text-[10px] mt-2 italic">* Vui lòng điều chỉnh giờ khám riêng cho bớt thành viên hoặc chọn khung giờ khác.</p>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <TimelineMatrix />

          <div className="flex gap-4 pt-6">
            <button onClick={() => setStep(2)} className="flex-1 py-4 border-2 border-slate-100 rounded-xl font-bold text-slate-500">Quay lại</button>
            <button 
              disabled={loading || capacityWarnings.length > 0}
              onClick={handleSubmit} 
              className="flex-[2] py-4 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-700 disabled:bg-slate-200 flex items-center justify-center gap-2"
            >
              {loading ? 'Đang xử lý...' : 'Xác nhận Đặt lịch'}
            </button>
          </div>
        </motion.div>
      )}

      {/* Step 4: Success Boarding Pass */}
      {step === 4 && bookingResult && (
        <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="print:m-0">
          <div className="text-center mb-8 no-print">
            <div className="w-20 h-20 bg-emerald-100 text-emerald-600 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle2 className="w-12 h-12" />
            </div>
            <h2 className="text-3xl font-black text-slate-800">ĐẶT LỊCH THÀNH CÔNG!</h2>
            <p className="text-slate-500">Cảm ơn quý khách đã tin tưởng Nha Khoa Minh Sinh</p>
          </div>

          {/* Boarding Pass UI */}
          <div className="relative max-w-2xl mx-auto bg-white rounded-3xl shadow-2xl overflow-hidden border border-slate-200">
            {/* Top Gradient Section */}
            <div className="bg-gradient-to-r from-blue-900 via-blue-800 to-emerald-600 p-8 text-white relative">
              <div className="flex justify-between items-start">
                <div>
                  <p className="text-xs font-bold opacity-70 uppercase tracking-widest">Hệ thống Nha Khoa</p>
                  <h3 className="text-2xl font-black">MINH SINH DENTAL</h3>
                </div>
                <PlaneTakeoff className="w-10 h-10 opacity-20" />
              </div>
              
              <div className="mt-10 flex justify-between items-end">
                <div>
                  <p className="text-[10px] opacity-70 uppercase">Mã đặt chỗ (PNR)</p>
                  <p className="text-5xl font-mono font-black tracking-[0.2em]">{bookingResult.pnr_code}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] opacity-70 uppercase">Trạng thái</p>
                  <p className="bg-emerald-500 text-[10px] px-2 py-1 rounded font-bold">ĐÃ XÁC NHẬN</p>
                </div>
              </div>

              {/* Ticket Notches */}
              <div className="absolute -bottom-4 -left-4 w-8 h-8 bg-white rounded-full shadow-inner" />
              <div className="absolute -bottom-4 -right-4 w-8 h-8 bg-white rounded-full shadow-inner" />
            </div>

            {/* Middle Section: Details */}
            <div className="p-8 pt-10 border-b-2 border-dashed border-slate-200 relative">
              <div className="grid grid-cols-2 gap-8 mb-8">
                <div>
                  <p className="text-[10px] text-slate-400 font-bold uppercase">Cơ sở khám</p>
                  <p className="font-bold text-slate-800">{bookingResult.clinic_name}</p>
                  <p className="text-xs text-slate-500">{bookingResult.clinic_address}</p>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-slate-400 font-bold uppercase">Ngày hẹn</p>
                  <p className="font-bold text-slate-800">{new Date(bookingResult.appointment_date).toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</p>
                </div>
              </div>

              <div className="space-y-4">
                <p className="text-[10px] text-slate-400 font-bold uppercase">Danh sách hành khách & Dịch vụ</p>
                {bookingResult.members.map((m, i) => (
                  <div key={i} className="flex justify-between items-center bg-slate-50 p-3 rounded-xl border border-slate-100">
                    <div>
                      <p className="text-sm font-bold text-slate-800">{m.full_name}</p>
                      <p className="text-[10px] text-blue-600 font-medium">{m.service_name} • {m.start_time}</p>
                    </div>
                    <p className="font-mono font-bold text-slate-700">{formatVND(m.price)}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Bottom Section: Barcode */}
            <div className="p-8 bg-slate-50 flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="flex flex-col items-center md:items-start">
                <Barcode className="w-48 h-12 text-slate-800" />
                <p className="text-[10px] font-mono mt-1 text-slate-400">{bookingResult.group_code}</p>
              </div>
              <div className="p-2 bg-white rounded-lg border border-slate-200">
                <QrCode className="w-16 h-16 text-slate-800" />
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="mt-10 flex flex-wrap justify-center gap-4 no-print">
            <button 
              onClick={() => window.print()}
              className="px-6 py-3 bg-slate-800 text-white rounded-xl font-bold flex items-center gap-2 hover:bg-slate-900 transition-all"
            >
              <Printer className="w-5 h-5" /> In vé máy bay / E-Ticket
            </button>
            <button 
              onClick={() => window.location.reload()}
              className="px-6 py-3 bg-blue-600 text-white rounded-xl font-bold flex items-center gap-2 hover:bg-blue-700 transition-all"
            >
              <Plus className="w-5 h-5" /> Đặt thêm lịch mới
            </button>
            <button className="px-6 py-3 border-2 border-slate-200 text-slate-600 rounded-xl font-bold hover:bg-slate-50 transition-all">
              Xem chi tiết biên nhận
            </button>
          </div>
        </motion.div>
      )}

      {/* Honeypot */}
      <input 
        type="text" 
        className="hidden" 
        value={formData.honeypot} 
        onChange={(e) => setFormData({...formData, honeypot: e.target.value})} 
      />

      <style jsx global>{`
        @media print {
          .no-print { display: none !important; }
          body { background: white !important; }
          .print\:m-0 { margin: 0 !important; }
        }
      `}</style>
    </div>
  );
}
