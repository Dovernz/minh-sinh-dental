'use client';

import React, { useState, useEffect, useMemo } from 'react';
import {
  Calendar,
  Clock,
  Users,
  Plus,
  Trash2,
  CheckCircle2,
  ChevronRight,
  AlertTriangle,
  Printer,
  Barcode,
  QrCode,
  PlaneTakeoff,
  Info,
  Zap,
  Sparkles,
  LayoutGrid,
  ListOrdered
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface Clinic {
  clinic_id?: number;
  id?: number;
  name: string;
  address?: string;
}

interface ServiceItem {
  service_id: number;
  code?: string;
  name: string;
  base_price?: string;
  unit?: string;
}

interface CategoryItem {
  category_id: number;
  name: string;
  estimate_time?: number;
  services: ServiceItem[];
}

interface TimeSlot {
  time: string;
  start_time?: string;
  available_chairs?: number;
  total_chairs?: number;
  booked_count?: number;
  is_full?: boolean;
  status?: 'available' | 'full' | 'limited';
  available_seats?: number;
}

interface Member {
  id: string;
  full_name: string;
  service_id: string;
  start_time: string;
}

interface BookingResult {
  pnr_code: string;
  group_code: string;
  clinic_name: string;
  clinic_address: string;
  appointment_date: string;
  members: {
    full_name: string;
    service_name: string;
    start_time: string;
  }[];
}

const TIME_STEPS = [
  "08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
  "13:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
  "17:30", "18:00", "18:30", "19:00"
];

const formatPNR = (pnr: string) => {
  if (!pnr) return "MS-XXXX";
  const clean = pnr.replace(/^MS-?/, '');
  const suffix = clean.slice(-4).toUpperCase();
  return `MS-${suffix}`;
};

export default function BookingForm() {
  const [step, setStep] = useState<number>(1);
  const [loading, setLoading] = useState<boolean>(false);
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [phoneError, setPhoneError] = useState<string>('');
  const [autoAllocationNotice, setAutoAllocationNotice] = useState<string>('');

  const [formData, setFormData] = useState({
    clinicId: '',
    date: new Date().toISOString().split('T')[0],
    selectedTime: '08:00',
    leaderName: '',
    leaderPhone: '',
    leaderServiceId: '',
    members: [] as Member[],
    honeypot: ''
  });

  const [bookingResult, setBookingResult] = useState<BookingResult | null>(null);

  // Tổng số người trong đoàn (Trưởng nhóm + Thành viên)
  const totalGroupSize = useMemo(() => 1 + formData.members.length, [formData.members]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [clinicsRes, servicesRes] = await Promise.all([
          fetch('/api/clinics/'),
          fetch('/api/service-tree/')
        ]);
        
        const clinicsData = await clinicsRes.json();
        const servicesData = await servicesRes.json();

        if (Array.isArray(clinicsData) && clinicsData.length > 0) {
          setClinics(clinicsData);
          const firstId = clinicsData[0].clinic_id ?? clinicsData[0].id;
          if (firstId != null) {
            setFormData(prev => ({ ...prev, clinicId: firstId.toString() }));
          }
        }

        if (Array.isArray(servicesData)) {
          setCategories(servicesData);
          for (const cat of servicesData) {
            if (cat.services && cat.services.length > 0 && cat.services[0]?.service_id != null) {
              setFormData(prev => ({ ...prev, leaderServiceId: cat.services[0].service_id.toString() }));
              break;
            }
          }
        }
      } catch (err) {
        console.error("Lỗi tải dữ liệu ban đầu:", err);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    if (formData.clinicId && formData.date) {
      const fetchSlots = async () => {
        try {
          const res = await fetch(`/api/available-slots/?clinic_id=${formData.clinicId}&date=${formData.date}`);
          const data = await res.json();
          const slots = Array.isArray(data) ? data : (data?.slots || []);
          setAvailableSlots(slots);
        } catch (err) {
          console.error("Lỗi tải lịch trống:", err);
          setAvailableSlots([]);
        }
      };
      fetchSlots();
    }
  }, [formData.clinicId, formData.date]);

  // --- THUẬT TOÁN TỰ ĐỘNG CHIA CA NỐI TIẾP (Smart Auto-Allocation) ---
  const autoAllocateSlots = (startSlotTime?: string) => {
    const startTime = startSlotTime || formData.selectedTime;
    console.log("[AutoAllocate] startTime:", startTime, "slots:", availableSlots.length);
    const startIndex = availableSlots.findIndex(s => (s.time === startTime || s.start_time === startTime || (s.time && s.time.startsWith(startTime))));
    
    if (startIndex === -1) {
      console.warn("[AutoAllocate] slot not found in availableSlots!", startTime);
      return;
    }

    let remainingToAllocate = [
      { type: 'leader', id: 'leader', name: formData.leaderName || 'Trưởng nhóm' },
      ...formData.members.map(m => ({ type: 'member', id: m.id, name: m.full_name || 'Thành viên' }))
    ];

    const newAllocations: { id: string, time: string, type: string }[] = [];
    let currentIdx = startIndex;

    while (remainingToAllocate.length > 0 && currentIdx < availableSlots.length) {
      const slot = availableSlots[currentIdx];
      const seats = slot.available_chairs ?? slot.available_seats ?? 5;
      const slotTime = slot.start_time || (slot.time && slot.time.includes(' - ') ? slot.time.split(' - ')[0] : slot.time) || '';
      
      if (seats > 0) {
        const batch = remainingToAllocate.splice(0, seats);
        batch.forEach(person => {
          newAllocations.push({ id: person.id, time: slotTime, type: person.type });
        });
      }
      currentIdx++;
    }

    // Cập nhật state dựa trên phân bổ mới
    const leaderAlloc = newAllocations.find(a => a.type === 'leader');
    const memberAllocations = newAllocations.filter(a => a.type === 'member');

    setFormData(prev => ({
      ...prev,
      selectedTime: leaderAlloc?.time || prev.selectedTime,
      members: prev.members.map(m => {
        const found = memberAllocations.find(ma => ma.id === m.id);
        return found ? { ...m, start_time: found.time } : m;
      })
    }));

    setAutoAllocationNotice(`Đã tự động sắp xếp ${totalGroupSize} khách vào các khung giờ nối tiếp nhau bắt đầu từ ${startTime}.`);
    setTimeout(() => setAutoAllocationNotice(''), 5000);
  };

  const handleGlobalTimeSelect = (time: string) => {
    const slot = availableSlots.find(s => s.time === time || s.start_time === time);
    const seats = slot?.available_chairs ?? slot?.available_seats ?? 5;

    if (seats >= totalGroupSize) {
      // Đủ chỗ cho cả đoàn vào 1 slot
      setFormData(prev => ({
        ...prev,
        selectedTime: time,
        members: prev.members.map(m => ({ ...m, start_time: time }))
      }));
      setAutoAllocationNotice(`Cả đoàn (${totalGroupSize} người) đã được xếp vào khung giờ ${time}.`);
    } else {
      // Không đủ chỗ, tự động chia ca
      autoAllocateSlots(time);
    }
  };

  const getRemainingSeatsForSlot = (time: string, excludeMemberId?: string) => {
    const slot = availableSlots.find(s => s.time === time || s.start_time === time);
    if (!slot) return 5;
    
    const totalSeats = slot.available_chairs ?? slot.available_seats ?? 5;
    
    // Tính số người trong nhóm hiện tại đang chiếm slot này
    let occupiedByGroup = 0;
    if (formData.selectedTime === time) occupiedByGroup++;
    formData.members.forEach(m => {
      if (m.start_time === time && m.id !== excludeMemberId) occupiedByGroup++;
    });

    return totalSeats - occupiedByGroup;
  };

  const calculateCapacityWarnings = () => {
    const counts: { [key: string]: number } = {};
    const groupTimes = [formData.selectedTime, ...formData.members.map(m => m.start_time)];
    groupTimes.forEach(t => { counts[t] = (counts[t] || 0) + 1; });

    const warnings: string[] = [];
    Object.keys(counts).forEach(time => {
      const slot = availableSlots.find(s => s.time === time || s.start_time === time);
      const seats = slot?.available_chairs ?? slot?.available_seats ?? 5;
      if (counts[time] > seats) {
        warnings.push(`Khung giờ ${time} chỉ còn ${seats} chỗ nhưng bạn đang xếp ${counts[time]} người.`);
      }
    });
    return warnings;
  };

  const getLeaderEstimateTime = (): number => {
    for (const cat of categories) {
      if (cat.services?.some(s => s.service_id.toString() === formData.leaderServiceId)) return cat.estimate_time || 30;
    }
    return 30;
  };

  const calculateEndTime = (startTime: string, minutes: number): string => {
    if (!startTime) return '';
    const [h, m] = startTime.split(':').map(Number);
    const total = (h || 0) * 60 + (m || 0) + minutes;
    return `${String(Math.floor(total / 60) % 24).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
  };

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value.replace(/[^0-9]/g, '');
    if (val.length <= 11) setFormData(prev => ({ ...prev, leaderPhone: val }));
  };

  const addMember = () => {
    if (formData.members.length >= 19) return; // Tối đa 20 người (gồm leader)
    
    let defaultServiceId = '';
    for (const cat of categories) {
      if (cat.services?.[0]?.service_id) {
        defaultServiceId = cat.services[0].service_id.toString();
        break;
      }
    }

    setFormData(prev => ({
      ...prev,
      members: [...prev.members, {
        id: Math.random().toString(36).substring(2, 9),
        full_name: '',
        service_id: defaultServiceId,
        start_time: prev.selectedTime
      }]
    }));
  };

  const removeMember = (id: string) => {
    setFormData(prev => ({ ...prev, members: prev.members.filter(m => m.id !== id) }));
  };

  const updateMember = (id: string, field: keyof Member, value: string) => {
    setFormData(prev => ({
      ...prev,
      members: prev.members.map(m => m.id === id ? { ...m, [field]: value } : m)
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.honeypot) return;
    if (calculateCapacityWarnings().length > 0) return;

    setLoading(true);
    try {
      const payload = {
        clinic_id: parseInt(formData.clinicId),
        appointment_date: formData.date,
        leader_name: formData.leaderName,
        leader_phone: formData.leaderPhone,
        leader_service_id: parseInt(formData.leaderServiceId),
        leader_start_time: formData.selectedTime,
        members: formData.members.map(m => ({
          full_name: m.full_name,
          service_id: parseInt(m.service_id),
          start_time: m.start_time
        }))
      };

      const res = await fetch('/api/bookings/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json();
      if (res.ok) {
        setBookingResult({
          pnr_code: data.pnr_code || 'MS-SUCCESS',
          group_code: data.group_code || 'GRP-01',
          clinic_name: clinics.find(c => (c.clinic_id ?? c.id)?.toString() === formData.clinicId)?.name || 'Nha Khoa Minh Sinh',
          clinic_address: clinics.find(c => (c.clinic_id ?? c.id)?.toString() === formData.clinicId)?.address || '',
          appointment_date: formData.date,
          members: [
            { full_name: formData.leaderName, service_name: getServiceName(formData.leaderServiceId), start_time: formData.selectedTime },
            ...formData.members.map(m => ({ full_name: m.full_name, service_name: getServiceName(m.service_id), start_time: m.start_time }))
          ]
        });
        setStep(4);
      } else {
        alert(data.error || 'Có lỗi xảy ra.');
      }
    } catch (err) {
      alert('Không thể kết nối đến máy chủ.');
    } finally {
      setLoading(false);
    }
  };

  const getServiceName = (serviceId: string) => {
    for (const cat of categories) {
      const found = cat.services?.find(s => s.service_id?.toString() === serviceId);
      if (found) return found.name;
    }
    return 'Dịch vụ nha khoa';
  };

  const renderServiceSelect = (value: string, onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void) => (
    <select
      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white text-gray-800 text-sm"
      value={value}
      onChange={onChange}
      required
    >
      <option value="">-- Chọn dịch vụ --</option>
      {categories.map(cat => (
        <optgroup key={cat.category_id} label={`${cat.name}`}>
          {cat.services.map(s => (
            <option key={s.service_id} value={s.service_id.toString()}>
              {s.name} ({cat.estimate_time || 30}p)
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  );

  const capacityWarnings = calculateCapacityWarnings();
  const perfectSlots = availableSlots.filter(s => (s.available_chairs ?? s.available_seats ?? 0) >= totalGroupSize);

  return (
    <div className="w-full max-w-7xl mx-auto p-4 sm:p-8 md:p-10 bg-white rounded-3xl shadow-2xl border border-gray-100">
      <input type="text" value={formData.honeypot} onChange={e => setFormData({ ...formData, honeypot: e.target.value })} className="hidden" />

      {/* Stepper */}
      {step < 4 && (
        <div className="max-w-2xl mx-auto flex items-center justify-between mb-10 relative">
          <div className="absolute top-1/2 left-0 w-full h-0.5 bg-gray-100 -translate-y-1/2 z-0" />
          {[1, 2, 3].map((s) => (
            <div key={s} className={`relative z-10 flex flex-col items-center gap-2 ${step >= s ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all duration-500 ${step >= s ? 'bg-blue-600 text-white shadow-lg shadow-blue-200 scale-110' : 'bg-gray-200 text-gray-500'}`}>
                {step > s ? <CheckCircle2 className="w-6 h-6" /> : s}
              </div>
              <span className="text-xs font-bold uppercase tracking-tighter hidden sm:block">
                {s === 1 ? 'Cơ sở' : s === 2 ? 'Thành viên' : 'Giờ khám'}
              </span>
            </div>
          ))}
        </div>
      )}

      <AnimatePresence mode="wait">
        {/* STEP 1: CLINIC & DATE */}
        {step === 1 && (
          <motion.div key="step1" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="space-y-6">
            <div className="bg-blue-50 p-6 rounded-2xl border border-blue-100">
              <h2 className="text-xl font-black text-blue-900 mb-4 flex items-center gap-2">
                <Calendar className="w-6 h-6" /> Chọn địa điểm & Thời gian
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-2">
                  <label className="text-sm font-bold text-gray-700">Cơ sở Nha Khoa</label>
                  <select
                    className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 outline-none transition-all"
                    value={formData.clinicId}
                    onChange={e => setFormData({ ...formData, clinicId: e.target.value })}
                  >
                    {clinics.map(c => <option key={c.clinic_id ?? c.id} value={(c.clinic_id ?? c.id)?.toString()}>{c.name}</option>)}
                  </select>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-bold text-gray-700">Ngày hẹn khám</label>
                  <input
                    type="date"
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full px-4 py-3 rounded-xl border-2 border-gray-200 focus:border-blue-500 outline-none transition-all"
                    value={formData.date}
                    onChange={e => setFormData({ ...formData, date: e.target.value })}
                  />
                </div>
              </div>
            </div>
            <div className="flex justify-end">
              <button onClick={() => setStep(2)} className="bg-blue-600 text-white px-8 py-4 rounded-2xl font-bold hover:bg-blue-700 transition-all flex items-center gap-2 shadow-xl shadow-blue-100">
                Tiếp theo <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 2: MEMBERS */}
        {step === 2 && (
          <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-black text-gray-800">Thông tin đoàn khám</h2>
              <div className="bg-amber-50 text-amber-700 px-4 py-2 rounded-full text-xs font-bold border border-amber-200 flex items-center gap-2 animate-pulse">
                <Sparkles className="w-4 h-4" /> Đoàn đông khách: Hệ thống sẽ tự động chia ca nối tiếp
              </div>
            </div>

            <div className="bg-white border-2 border-blue-100 rounded-2xl p-6 space-y-4 shadow-sm">
              <div className="flex items-center gap-2 text-blue-600 font-bold text-sm uppercase tracking-widest">
                <Users className="w-4 h-4" /> Trưởng nhóm (Người liên hệ)
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <input
                  type="text"
                  placeholder="Họ và tên trưởng nhóm"
                  className="px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.leaderName}
                  onChange={e => setFormData({ ...formData, leaderName: e.target.value })}
                />
                <input
                  type="text"
                  placeholder="Số điện thoại"
                  className="px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 outline-none"
                  value={formData.leaderPhone}
                  onChange={handlePhoneChange}
                />
              </div>
              {renderServiceSelect(formData.leaderServiceId, e => setFormData({ ...formData, leaderServiceId: e.target.value }))}
            </div>

            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h3 className="font-bold text-gray-700">Thành viên đi cùng ({formData.members.length})</h3>
                <button onClick={addMember} className="flex items-center gap-2 bg-green-50 text-green-700 px-4 py-2 rounded-xl font-bold hover:bg-green-100 transition-all border border-green-200">
                  <Plus className="w-4 h-4" /> Thêm người
                </button>
              </div>

              <div className="grid grid-cols-1 gap-4">
                {formData.members.map((m, idx) => (
                  <motion.div layout key={m.id} className="bg-gray-50 p-4 rounded-2xl border border-gray-200 flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                    <div className="w-8 h-8 bg-white rounded-full flex items-center justify-center text-xs font-bold border border-gray-300">{idx + 1}</div>
                    <input
                      type="text"
                      placeholder="Tên thành viên"
                      className="flex-1 px-3 py-2 rounded-lg border border-gray-200 text-sm outline-none"
                      value={m.full_name}
                      onChange={e => updateMember(m.id, 'full_name', e.target.value)}
                    />
                    <div className="flex-1 w-full">
                      {renderServiceSelect(m.service_id, e => updateMember(m.id, 'service_id', e.target.value))}
                    </div>
                    <button onClick={() => removeMember(m.id)} className="p-2 text-red-400 hover:text-red-600 transition-colors">
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </motion.div>
                ))}
              </div>
            </div>

            <div className="flex justify-between pt-6">
              <button onClick={() => setStep(1)} className="px-8 py-4 text-gray-500 font-bold hover:bg-gray-100 rounded-2xl transition-all">Quay lại</button>
              <button onClick={() => setStep(3)} className="bg-blue-600 text-white px-10 py-4 rounded-2xl font-bold hover:bg-blue-700 transition-all shadow-xl shadow-blue-100">Tiếp tục</button>
            </div>
          </motion.div>
        )}

        {/* STEP 3: SMART TIME SELECTION */}
        {step === 3 && (
          <motion.div key="step3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-6">
            <div className="flex flex-col gap-4">
              <h2 className="text-2xl font-black text-gray-800">Chọn giờ khám thông minh</h2>
              
              {/* Smart Suggestions */}
              {perfectSlots.length > 0 && (
                <div className="bg-green-50 border border-green-200 p-4 rounded-2xl">
                  <p className="text-sm font-bold text-green-800 mb-2 flex items-center gap-2">
                    <Sparkles className="w-4 h-4" /> Khung giờ còn đủ chỗ cho cả đoàn ({totalGroupSize} người):
                  </p>
                  <div className="flex flex-wrap gap-2">
                    {perfectSlots.slice(0, 5).map(s => (
                      <button
                        key={s.time}
                        onClick={() => handleGlobalTimeSelect(s.time || s.start_time || '')}
                        className="px-3 py-1.5 bg-white border border-green-300 text-green-700 rounded-lg text-xs font-bold hover:bg-green-600 hover:text-white transition-all"
                      >
                        {s.time || s.start_time}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {autoAllocationNotice && (
                <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="bg-blue-50 border border-blue-200 text-blue-900 p-4 rounded-2xl text-sm font-bold flex items-center gap-3 shadow-sm">
                  <Zap className="w-5 h-5 text-blue-600 fill-blue-600 shrink-0" /> <span>{autoAllocationNotice}</span>
                </motion.div>
              )}
            </div>

            {/* Time Grid */}
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <label className="text-sm font-black text-gray-700 uppercase tracking-widest">Bấm chọn giờ bắt đầu cho đoàn:</label>
                <button 
                  onClick={() => autoAllocateSlots()}
                  className="text-xs bg-blue-50 text-blue-700 px-3 py-1.5 rounded-lg font-bold border border-blue-200 flex items-center gap-1 hover:bg-blue-600 hover:text-white transition-all"
                >
                  <Zap className="w-3 h-3" /> Tự động chia ca tối ưu
                </button>
              </div>
              <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-8 gap-2">
                {TIME_STEPS.map(time => {
                  const slot = availableSlots.find(s => s.time === time || s.start_time === time);
                  const seats = slot?.available_chairs ?? slot?.available_seats ?? 0;
                  const isFull = seats <= 0;
                  const isSelected = formData.selectedTime === time;

                  return (
                    <button
                      key={time}
                      disabled={isFull}
                      onClick={() => handleGlobalTimeSelect(time)}
                      className={`relative p-3 rounded-xl border-2 transition-all flex flex-col items-center gap-1 ${
                        isSelected ? 'border-blue-600 bg-blue-50 ring-2 ring-blue-200' : 
                        isFull ? 'bg-gray-50 border-gray-100 opacity-40 cursor-not-allowed' : 'border-gray-100 hover:border-blue-300'
                      }`}
                    >
                      <span className={`text-sm font-bold ${isSelected ? 'text-blue-700' : 'text-gray-700'}`}>{time}</span>
                      <span className={`text-[10px] font-medium ${seats < 3 ? 'text-red-500' : 'text-gray-400'}`}>
                        {isFull ? 'Hết chỗ' : `${seats} ghế`}
                      </span>
                      {isSelected && <div className="absolute -top-2 -right-2 bg-blue-600 text-white rounded-full p-0.5"><CheckCircle2 className="w-3 h-3" /></div>}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Timeline Matrix */}
            <div className="bg-white rounded-3xl p-6 text-slate-800 shadow-md border border-blue-200">
              <div className="flex items-center justify-between mb-6 pb-4 border-b border-blue-100">
                <h3 className="text-lg font-bold flex items-center gap-2 text-blue-900">
                  <ListOrdered className="w-5 h-5 text-blue-600" /> Lịch trình chi tiết của đoàn
                </h3>
                <div className="text-xs text-slate-500 font-medium">Tùy chỉnh giờ riêng cho từng khách nếu cần</div>
              </div>
              
              <div className="space-y-3">
                {/* Leader Row */}
                <div className="flex items-center gap-4 bg-blue-50/70 p-3.5 rounded-2xl border border-blue-100 shadow-sm hover:bg-blue-50 transition-colors">
                  <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-sm ring-2 ring-blue-100">TN</div>
                  <div className="flex-1">
                    <div className="text-sm font-bold text-slate-900">{formData.leaderName || 'Trưởng nhóm'}</div>
                    <div className="text-[10px] text-blue-700 font-bold uppercase tracking-wider">{getServiceName(formData.leaderServiceId)}</div>
                  </div>
                  <select 
                    className="bg-white border border-blue-200 text-slate-800 rounded-xl px-3 py-1.5 text-xs font-bold outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 shadow-sm cursor-pointer"
                    value={formData.selectedTime}
                    onChange={e => setFormData({...formData, selectedTime: e.target.value})}
                  >
                    {TIME_STEPS.map(t => {
                      const rem = getRemainingSeatsForSlot(t);
                      return <option key={t} value={t} disabled={rem <= 0}>{t} ({rem} chỗ)</option>;
                    })}
                  </select>
                </div>

                {/* Members Rows */}
                {formData.members.map((m, idx) => (
                  <div key={m.id} className="flex items-center gap-4 bg-slate-50/80 p-3.5 rounded-2xl border border-slate-200/80 shadow-sm hover:bg-slate-50 transition-colors">
                    <div className="w-10 h-10 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-sm shadow-sm ring-2 ring-slate-100">{idx + 1}</div>
                    <div className="flex-1">
                      <div className="text-sm font-bold text-slate-900">{m.full_name || `Thành viên ${idx + 1}`}</div>
                      <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">{getServiceName(m.service_id)}</div>
                    </div>
                    <select 
                      className="bg-white border border-slate-200 text-slate-800 rounded-xl px-3 py-1.5 text-xs font-bold outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 shadow-sm cursor-pointer"
                      value={m.start_time}
                      onChange={e => updateMember(m.id, 'start_time', e.target.value)}
                    >
                      {TIME_STEPS.map(t => {
                        const rem = getRemainingSeatsForSlot(t, m.id);
                        return <option key={t} value={t} disabled={rem <= 0}>{t} ({rem} chỗ)</option>;
                      })}
                    </select>
                  </div>
                ))}
              </div>
            </div>

            {/* Capacity Warnings */}
            {capacityWarnings.length > 0 && (
              <div className="p-4 bg-red-50 border-2 border-red-200 rounded-2xl space-y-2">
                <div className="flex items-center gap-2 text-red-700 font-black text-sm">
                  <AlertTriangle className="w-5 h-5" /> PHÁT HIỆN QUÁ TẢI
                </div>
                {capacityWarnings.map((w, i) => <p key={i} className="text-xs text-red-600 font-medium">• {w}</p>)}
                <button onClick={() => autoAllocateSlots()} className="w-full mt-2 py-2 bg-red-600 text-white rounded-xl text-xs font-bold hover:bg-red-700 transition-all">
                  Bấm để tự động chia lại ca hợp lệ
                </button>
              </div>
            )}

            <div className="flex justify-between pt-6">
              <button onClick={() => setStep(2)} className="px-8 py-4 text-gray-500 font-bold hover:bg-gray-100 rounded-2xl transition-all">Quay lại</button>
              <button 
                disabled={loading || capacityWarnings.length > 0} 
                onClick={handleSubmit}
                className="bg-blue-600 text-white px-10 py-4 rounded-2xl font-bold hover:bg-blue-700 transition-all shadow-xl shadow-blue-200 disabled:opacity-50 disabled:grayscale"
              >
                {loading ? 'Đang xử lý...' : 'Xác nhận Đặt lịch'}
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 4: BOARDING PASS */}
        {step === 4 && bookingResult && (
          <motion.div key="step4" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="max-w-3xl mx-auto space-y-8">
            <div className="text-center space-y-2">
              <div className="w-20 h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-4 shadow-inner">
                <CheckCircle2 className="w-10 h-10" />
              </div>
              <h2 className="text-3xl font-black text-gray-900">Đặt lịch thành công!</h2>
              <p className="text-gray-500 font-medium">Vui lòng lưu lại Boarding Pass để làm thủ tục tại quầy.</p>
            </div>

            <div className="relative group">
              {/* Decorative holes for ticket look */}
              <div className="absolute top-1/2 -left-4 w-8 h-8 bg-white rounded-full -translate-y-1/2 z-20 border-r border-gray-100" />
              <div className="absolute top-1/2 -right-4 w-8 h-8 bg-white rounded-full -translate-y-1/2 z-20 border-l border-gray-100" />
              
              <div className="bg-gradient-to-br from-indigo-900 via-blue-900 to-blue-800 text-white rounded-3xl overflow-hidden shadow-2xl border border-blue-700">
                <div className="p-8 space-y-8">
                  <div className="flex justify-between items-start border-b border-white/10 pb-6">
                    <div>
                      <div className="text-[10px] font-black uppercase tracking-[0.3em] text-blue-300 mb-1">Minh Sinh Dental Clinic</div>
                      <h3 className="text-2xl font-black tracking-tighter">E-BOARDING PASS</h3>
                    </div>
                    <div className="text-right">
                      <div className="text-[10px] font-bold text-blue-300 uppercase mb-1">Mã đặt chỗ (PNR)</div>
                      <div className="text-3xl font-mono font-black text-amber-400">{formatPNR(bookingResult.pnr_code)}</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
                    <div className="space-y-1">
                      <div className="text-[10px] font-bold text-blue-300 uppercase">Cơ sở khám</div>
                      <div className="font-black text-sm">{bookingResult.clinic_name}</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-[10px] font-bold text-blue-300 uppercase">Ngày hẹn</div>
                      <div className="font-black text-sm">{bookingResult.appointment_date}</div>
                    </div>
                    <div className="space-y-1 col-span-2 md:col-span-1">
                      <div className="text-[10px] font-bold text-blue-300 uppercase">Địa chỉ</div>
                      <div className="font-medium text-[11px] leading-tight text-blue-100">{bookingResult.clinic_address}</div>
                    </div>
                  </div>

                  <div className="space-y-4">
                    <div className="text-[10px] font-black text-blue-300 uppercase tracking-widest">Danh sách hành khách & Giờ khám</div>
                    <div className="grid grid-cols-1 gap-2">
                      {bookingResult.members.map((m, i) => (
                        <div key={i} className="flex items-center justify-between bg-white/10 p-3 rounded-xl backdrop-blur-md border border-white/5">
                          <div>
                            <div className="text-sm font-black">{m.full_name}</div>
                            <div className="text-[10px] text-blue-200">{m.service_name}</div>
                          </div>
                          <div className="text-right">
                            <div className="text-xs font-mono font-black text-amber-300 bg-amber-400/10 px-2 py-1 rounded-lg border border-amber-400/20">
                              {m.start_time}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="pt-6 border-t border-white/10 flex items-center justify-between">
                    <div className="flex items-center gap-3 opacity-60">
                      <Barcode className="w-12 h-12" />
                      <div className="font-mono text-[10px] tracking-widest">MS-{bookingResult.group_code}</div>
                    </div>
                    <div className="bg-white p-2 rounded-xl">
                      <QrCode className="w-12 h-12 text-blue-900" />
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <button onClick={() => window.print()} className="flex-1 px-8 py-4 bg-gray-100 text-gray-700 font-bold rounded-2xl hover:bg-gray-200 transition-all flex items-center justify-center gap-2">
                <Printer className="w-5 h-5" /> In vé điện tử
              </button>
              <button 
                onClick={() => window.location.reload()} 
                className="flex-1 px-8 py-4 bg-blue-600 text-white font-bold rounded-2xl hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-xl shadow-blue-100"
              >
                <PlaneTakeoff className="w-5 h-5" /> Đặt lịch mới
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}