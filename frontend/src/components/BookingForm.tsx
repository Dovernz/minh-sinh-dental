'use client';

import React, { useState, useEffect } from 'react';
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
  Info
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
  services: ServiceItem[];
}

interface TimeSlot {
  time: string;
  status: 'available' | 'full' | 'limited';
  available_seats: number;
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
          // Find first available service ID
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
          const res = await fetch(`/api/daily-schedule/?clinic_id=${formData.clinicId}&date=${formData.date}`);
          const data = await res.json();
          if (data && data.slots) {
            setAvailableSlots(data.slots);
          } else {
            setAvailableSlots([]);
          }
        } catch (err) {
          console.error("Lỗi tải lịch trống:", err);
          setAvailableSlots([]);
        }
      };
      fetchSlots();
    }
  }, [formData.clinicId, formData.date]);

  const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value.replace(/[^0-9]/g, '');
    if (val.length <= 11) {
      setFormData(prev => ({ ...prev, leaderPhone: val }));
      if (phoneError) setPhoneError('');
    }
  };

  const handleStep2Next = (e: React.FormEvent) => {
    e.preventDefault();
    if (!/^[0-9]{10,11}$/.test(formData.leaderPhone)) {
      setPhoneError("Số điện thoại phải từ 10 đến 11 chữ số hợp lệ.");
      return;
    }
    setPhoneError("");
    setStep(3);
  };

  const addMember = () => {
    let defaultServiceId = '';
    for (const cat of categories) {
      if (cat.services && cat.services.length > 0 && cat.services[0]?.service_id != null) {
        defaultServiceId = cat.services[0].service_id.toString();
        break;
      }
    }
    setFormData(prev => ({
      ...prev,
      members: [
        ...prev.members,
        {
          id: Math.random().toString(36).substring(2, 9),
          full_name: '',
          service_id: defaultServiceId,
          start_time: formData.selectedTime
        }
      ]
    }));
  };

  const removeMember = (id: string) => {
    setFormData(prev => ({
      ...prev,
      members: prev.members.filter(m => m.id !== id)
    }));
  };

  const updateMember = (id: string, field: keyof Member, value: string) => {
    setFormData(prev => ({
      ...prev,
      members: prev.members.map(m => m.id === id ? { ...m, [field]: value } : m)
    }));
  };

  const handleGlobalTimeSelect = (time: string) => {
    setFormData(prev => ({
      ...prev,
      selectedTime: time,
      members: prev.members.map(m => ({ ...m, start_time: time }))
    }));
  };

  const calculateCapacityWarnings = () => {
    const counts: { [key: string]: number } = {};
    const totalGroupTime = [
      { time: formData.selectedTime },
      ...formData.members.map(m => ({ time: m.start_time }))
    ];

    totalGroupTime.forEach(item => {
      counts[item.time] = (counts[item.time] || 0) + 1;
    });

    const warnings: string[] = [];
    Object.keys(counts).forEach(time => {
      const slotInfo = availableSlots.find(s => s.time === time);
      if (slotInfo && counts[time] > slotInfo.available_seats) {
        warnings.push(`Khung giờ ${time}: Số lượng người đăng ký (${counts[time]}) vượt quá chỗ trống hiện có (${slotInfo.available_seats}).`);
      }
    });

    return warnings;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.honeypot) return;

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
          pnr_code: data.pnr_code || 'MS-9999',
          group_code: data.group_code || 'GRP-01',
          clinic_name: clinics.find(c => (c.clinic_id ?? c.id)?.toString() === formData.clinicId)?.name || 'Nha Khoa Minh Sinh',
          clinic_address: clinics.find(c => (c.clinic_id ?? c.id)?.toString() === formData.clinicId)?.address || '',
          appointment_date: formData.date,
          members: [
            {
              full_name: formData.leaderName,
              service_name: getServiceName(formData.leaderServiceId),
              start_time: formData.selectedTime
            },
            ...formData.members.map(m => ({
              full_name: m.full_name,
              service_name: getServiceName(m.service_id),
              start_time: m.start_time
            }))
          ]
        });
        setStep(4);
      } else {
        alert(data.error || 'Có lỗi xảy ra khi đặt lịch.');
      }
    } catch (err) {
      console.error("Lỗi đặt lịch:", err);
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

  const renderServiceSelect = (value: string, onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void, required = false) => (
    <select
      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-gray-800"
      value={value}
      onChange={onChange}
      required={required}
    >
      <option value="">-- Chọn dịch vụ nha khoa --</option>
      {categories.map(cat => (
        cat.services && cat.services.length > 0 && (
          <optgroup key={cat.category_id} label={cat.name}>
            {cat.services.map(s => (
              <option key={s.service_id} value={s.service_id?.toString() || ''}>
                {s.name}
              </option>
            ))}
          </optgroup>
        )
      ))}
    </select>
  );

  const capacityWarnings = calculateCapacityWarnings();

  return (
    <div className="max-w-4xl mx-auto p-4 sm:p-6 bg-white rounded-2xl shadow-xl border border-gray-100">
      {/* Hidden Honeypot */}
      <input
        type="text"
        name="honeypot"
        value={formData.honeypot}
        onChange={e => setFormData({ ...formData, honeypot: e.target.value })}
        style={{ display: 'none' }}
        tabIndex={-1}
        autoComplete="off"
      />

      {/* Stepper Header */}
      {step < 4 && (
        <div className="flex items-center justify-between mb-8 pb-4 border-b border-gray-100">
          <div className="flex items-center space-x-2">
            <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}`}>1</span>
            <span className="text-sm font-medium hidden sm:inline text-gray-700">Cơ sở & Ngày</span>
          </div>
          <ChevronRight className="w-4 h-4 text-gray-400" />
          <div className="flex items-center space-x-2">
            <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}`}>2</span>
            <span className="text-sm font-medium hidden sm:inline text-gray-700">Nhóm & Dịch vụ</span>
          </div>
          <ChevronRight className="w-4 h-4 text-gray-400" />
          <div className="flex items-center space-x-2">
            <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}`}>3</span>
            <span className="text-sm font-medium hidden sm:inline text-gray-700">Giờ khám</span>
          </div>
        </div>
      )}

      <AnimatePresence mode="wait">
        {/* STEP 1 */}
        {step === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <Calendar className="w-5 h-5 text-blue-600" />
              Chọn cơ sở nha khoa và ngày hẹn
            </h2>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Cơ sở Nha Khoa Minh Sinh</label>
              <select
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none bg-white text-gray-800"
                value={formData.clinicId}
                onChange={e => setFormData({ ...formData, clinicId: e.target.value })}
              >
                {clinics.map(clinic => {
                  const cId = (clinic.clinic_id ?? clinic.id ?? '').toString();
                  return (
                    <option key={cId} value={cId}>
                      {clinic.name} {clinic.address ? `- ${clinic.address}` : ''}
                    </option>
                  );
                })}
              </select>
            </div>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-2">Ngày khám dự kiến</label>
              <input
                type="date"
                min={new Date().toISOString().split('T')[0]}
                className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none text-gray-800"
                value={formData.date}
                onChange={e => setFormData({ ...formData, date: e.target.value })}
              />
            </div>

            <div className="flex justify-end pt-4">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition flex items-center gap-2 shadow-lg shadow-blue-500/20"
              >
                Tiếp tục <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 2 */}
        {step === 2 && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-600" />
              Thông tin trưởng nhóm & Thành viên
            </h2>

            <form onSubmit={handleStep2Next} className="space-y-6">
              <div className="bg-blue-50/50 p-4 rounded-xl border border-blue-100 space-y-4">
                <h3 className="font-semibold text-blue-900 text-sm uppercase tracking-wider">Thông tin trưởng nhóm</h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Họ và tên *</label>
                    <input
                      type="text"
                      required
                      placeholder="Nguyễn Văn A"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none text-gray-800"
                      value={formData.leaderName}
                      onChange={e => setFormData({ ...formData, leaderName: e.target.value })}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Số điện thoại (10-11 số) *</label>
                    <input
                      type="text"
                      maxLength={11}
                      required
                      placeholder="0912345678"
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none text-gray-800"
                      value={formData.leaderPhone}
                      onChange={handlePhoneChange}
                    />
                    {phoneError && <p className="text-red-500 text-xs mt-1">{phoneError}</p>}
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Dịch vụ nha khoa *</label>
                  {renderServiceSelect(
                    formData.leaderServiceId,
                    e => setFormData({ ...formData, leaderServiceId: e.target.value }),
                    true
                  )}
                </div>
              </div>

              {/* Members Section */}
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-gray-800 text-sm uppercase tracking-wider">Thành viên đi cùng ({formData.members.length})</h3>
                  <button
                    type="button"
                    onClick={addMember}
                    className="px-3 py-1.5 bg-green-600 text-white text-sm font-medium rounded-lg hover:bg-green-700 transition flex items-center gap-1 shadow-sm"
                  >
                    <Plus className="w-4 h-4" /> Thêm thành viên
                  </button>
                </div>

                {formData.members.map((member, index) => (
                  <div key={member.id} className="p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3 relative">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-gray-500 uppercase">Thành viên #{index + 1}</span>
                      <button
                        type="button"
                        onClick={() => removeMember(member.id)}
                        className="text-red-500 hover:text-red-700 p-1 transition"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Họ và tên</label>
                        <input
                          type="text"
                          required
                          placeholder="Họ tên thành viên"
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm bg-white text-gray-800"
                          value={member.full_name}
                          onChange={e => updateMember(member.id, 'full_name', e.target.value)}
                        />
                      </div>
                      <div>
                        <label className="block text-xs font-medium text-gray-600 mb-1">Dịch vụ</label>
                        {renderServiceSelect(
                          member.service_id,
                          e => updateMember(member.id, 'service_id', e.target.value),
                          true
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-between pt-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-xl hover:bg-gray-200 transition"
                >
                  Quay lại
                </button>
                <button
                  type="submit"
                  className="px-6 py-3 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition flex items-center gap-2 shadow-lg shadow-blue-500/20"
                >
                  Tiếp tục <ChevronRight className="w-4 h-4" />
                </button>
              </div>
            </form>
          </motion.div>
        )}

        {/* STEP 3 */}
        {step === 3 && (
          <motion.div
            key="step3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <h2 className="text-xl font-bold text-gray-800 flex items-center gap-2">
              <Clock className="w-5 h-5 text-blue-600" />
              Chọn khung giờ khám & Xác nhận
            </h2>

            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">Chọn giờ khám chung cho nhóm:</label>
              <div className="grid grid-cols-4 sm:grid-cols-5 md:grid-cols-10 gap-2">
                {TIME_STEPS.map(time => {
                  const slotInfo = availableSlots.find(s => s.time === time);
                  const isFull = slotInfo && slotInfo.status === 'full';
                  const isSelected = formData.selectedTime === time;

                  return (
                    <button
                      key={time}
                      type="button"
                      disabled={isFull}
                      onClick={() => handleGlobalTimeSelect(time)}
                      className={`py-2 px-1 text-xs font-semibold rounded-lg border transition text-center ${
                        isSelected
                          ? 'bg-blue-600 text-white border-blue-600 shadow-md'
                          : isFull
                          ? 'bg-gray-100 text-gray-400 border-gray-200 cursor-not-allowed line-through'
                          : 'bg-white text-gray-700 border-gray-200 hover:border-blue-400'
                      }`}
                    >
                      {time}
                    </button>
                  );
                })}
              </div>
            </div>

            {formData.members.length > 0 && (
              <div className="space-y-3 pt-2">
                <h3 className="text-sm font-semibold text-gray-700">Tùy chỉnh giờ riêng cho từng thành viên (nếu cần):</h3>
                {formData.members.map((m, idx) => (
                  <div key={m.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-200 text-sm">
                    <span className="font-medium text-gray-800">{idx + 1}. {m.full_name || 'Thành viên chưa có tên'}</span>
                    <select
                      className="px-3 py-1.5 border border-gray-300 rounded-lg bg-white text-gray-800 text-xs"
                      value={m.start_time}
                      onChange={e => updateMember(m.id, 'start_time', e.target.value)}
                    >
                      {TIME_STEPS.map(t => (
                        <option key={t} value={t}>{t}</option>
                      ))}
                    </select>
                  </div>
                ))}
              </div>
            )}

            {/* Capacity Warnings */}
            {capacityWarnings.length > 0 && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl space-y-1">
                <div className="flex items-center gap-2 text-amber-800 font-semibold text-sm">
                  <AlertTriangle className="w-4 h-4" /> Cảnh báo sức chứa
                </div>
                {capacityWarnings.map((warn, i) => (
                  <p key={i} className="text-xs text-amber-700">{warn}</p>
                ))}
              </div>
            )}

            {/* Timeline Matrix */}
            <div className="p-4 bg-gray-50 rounded-xl border border-gray-200 space-y-3">
              <h3 className="text-sm font-semibold text-gray-800 flex items-center gap-2">
                <Info className="w-4 h-4 text-blue-600" /> Lịch trình nhóm dự kiến
              </h3>
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs p-2 bg-white rounded-lg border border-gray-100">
                  <span className="font-medium text-gray-700">{formData.leaderName || 'Trưởng nhóm'} (Trưởng nhóm)</span>
                  <span className="text-blue-600 font-bold">{formData.selectedTime}</span>
                </div>
                {formData.members.map((m, i) => (
                  <div key={i} className="flex justify-between items-center text-xs p-2 bg-white rounded-lg border border-gray-100">
                    <span className="font-medium text-gray-700">{m.full_name || `Thành viên #${i + 1}`}</span>
                    <span className="text-blue-600 font-bold">{m.start_time}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-between pt-4">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-xl hover:bg-gray-200 transition"
              >
                Quay lại
              </button>
              <button
                type="button"
                disabled={loading}
                onClick={handleSubmit}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition flex items-center gap-2 shadow-lg shadow-blue-500/20 disabled:opacity-50"
              >
                {loading ? 'Đang xử lý...' : 'Xác nhận Đặt lịch'} <CheckCircle2 className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 4: BOARDING PASS / E-TICKET */}
        {step === 4 && bookingResult && (
          <motion.div
            key="step4"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="space-y-6"
          >
            <div className="text-center space-y-2">
              <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 text-green-600 rounded-full mb-2">
                <CheckCircle2 className="w-6 h-6" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800">Đặt lịch thành công!</h2>
              <p className="text-sm text-gray-500">Vé điện tử (Boarding Pass) của bạn đã được phát hành.</p>
            </div>

            {/* Boarding Pass Card */}
            <div className="bg-gradient-to-br from-blue-900 to-indigo-900 text-white rounded-2xl shadow-xl overflow-hidden border border-blue-800">
              <div className="p-6 sm:p-8 space-y-6">
                <div className="flex justify-between items-start border-b border-blue-800/60 pb-4">
                  <div>
                    <span className="text-xs uppercase tracking-widest text-blue-300 font-semibold">Nha Khoa Minh Sinh</span>
                    <h3 className="text-xl font-extrabold tracking-tight mt-1">E-BOARDING PASS</h3>
                  </div>
                  <div className="text-right">
                    <span className="text-xs text-blue-300 block">MÃ ĐẶT CHỖ (PNR)</span>
                    <span className="text-2xl font-mono font-bold text-amber-400">{formatPNR(bookingResult.pnr_code)}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 text-sm">
                  <div>
                    <span className="text-xs text-blue-300 block">CƠ SỞ</span>
                    <span className="font-semibold">{bookingResult.clinic_name}</span>
                  </div>
                  <div>
                    <span className="text-xs text-blue-300 block">ĐỊA CHỈ</span>
                    <span className="font-semibold truncate block">{bookingResult.clinic_address || 'Hệ thống Nha khoa'}</span>
                  </div>
                  <div>
                    <span className="text-xs text-blue-300 block">NGÀY HẸN</span>
                    <span className="font-semibold">{bookingResult.appointment_date}</span>
                  </div>
                </div>

                {/* Members list in boarding pass */}
                <div className="space-y-3 pt-2">
                  <span className="text-xs uppercase tracking-wider text-blue-300 font-semibold block">Danh sách hành khách / dịch vụ</span>
                  <div className="space-y-2">
                    {bookingResult.members.map((m, idx) => (
                      <div key={idx} className="bg-white/10 p-3 rounded-xl flex items-center justify-between text-sm backdrop-blur-sm">
                        <div>
                          <p className="font-bold text-white">{m.full_name}</p>
                          <p className="text-xs text-blue-200">{m.service_name}</p>
                        </div>
                        <div className="text-right">
                          <span className="inline-block px-2.5 py-1 bg-green-500/20 text-green-300 border border-green-500/30 rounded-full text-xs font-semibold mb-1">
                            Đã xác nhận
                          </span>
                          <p className="text-xs font-mono text-amber-300">Giờ: {m.start_time}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-blue-800/60 flex items-center justify-between text-xs text-blue-300">
                  <div className="flex items-center gap-2">
                    <Barcode className="w-8 h-8 text-white/80" />
                    <span className="font-mono">MS-BARCODE-SYSTEM</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <QrCode className="w-8 h-8 text-white/80" />
                  </div>
                </div>
              </div>
            </div>

            <div className="flex justify-center gap-4 pt-4">
              <button
                type="button"
                onClick={() => window.print()}
                className="px-6 py-3 bg-gray-100 text-gray-700 font-medium rounded-xl hover:bg-gray-200 transition flex items-center gap-2"
              >
                <Printer className="w-4 h-4" /> In vé máy bay
              </button>
              <button
                type="button"
                onClick={() => {
                  setStep(1);
                  setBookingResult(null);
                  setFormData({
                    clinicId: clinics[0]?.id?.toString() || '',
                    date: new Date().toISOString().split('T')[0],
                    selectedTime: '08:00',
                    leaderName: '',
                    leaderPhone: '',
                    leaderServiceId: '',
                    members: [],
                    honeypot: ''
                  });
                }}
                className="px-6 py-3 bg-blue-600 text-white font-medium rounded-xl hover:bg-blue-700 transition flex items-center gap-2 shadow-lg shadow-blue-500/20"
              >
                Đặt thêm lịch mới <PlaneTakeoff className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}