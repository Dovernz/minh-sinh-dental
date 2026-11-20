'use client';

import React, { useState, useEffect, useMemo } from 'react';
import { Calendar, Clock, Users, Plus, Trash2, CheckCircle2, ChevronRight, ChevronLeft, AlertTriangle, Printer, Barcode, QrCode, PlaneTakeoff, Info, Zap, Sparkles, LayoutGrid, ListOrdered, Phone, User, Loader2, AlertCircle, CalendarPlus } from 'lucide-react';
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
  phone: string;
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
    phone?: string;
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

// Kiểm tra tên chứa số hoặc ký tự đặc biệt (chỉ cho phép chữ cái Unicode và khoảng trắng)
const hasInvalidNameChars = (val: string): boolean => {
  return /[^\p{L}\s]/u.test(val);
};

const NAME_INVALID_WARNING = "⚠️ Họ và tên chỉ được chứa chữ cái và dấu cách, không chứa số hoặc ký tự đặc biệt.";

// Hàm lọc SĐT: Chỉ cho phép chữ số, tối đa 11 số
const sanitizePhone = (val: string): string => {
  return val.replace(/\D/g, '').slice(0, 11);
};

export default function BookingForm() {
  const [step, setStep] = useState<number>(() => {
    if (typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('test_step') === '4') return 4;
    return 1;
  });
  const [loading, setLoading] = useState<boolean>(false);
  const [clinics, setClinics] = useState<Clinic[]>([]);
  const [categories, setCategories] = useState<CategoryItem[]>([]);
  const [availableSlots, setAvailableSlots] = useState<TimeSlot[]>([]);
  const [autoAllocationNotice, setAutoAllocationNotice] = useState<string>('');

  // State lỗi validation cho từng trường
  const [errors, setErrors] = useState<{
    leaderName?: string;
    leaderPhone?: string;
    members?: Record<string, { full_name?: string; phone?: string }>;
    submit?: string;
  }>({});

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

  const [bookingResult, setBookingResult] = useState<BookingResult | null>(() => {
    if (typeof window !== 'undefined' && new URLSearchParams(window.location.search).get('test_step') === '4') {
      return {
        pnr_code: 'MS-8K92L1',
        group_code: 'GRP-MINHSINH',
        clinic_name: 'Nha Khoa Minh Sinh - Cơ sở Phố Huế',
        clinic_address: '123 Phố Huế, Hai Bà Trưng, Hà Nội',
        appointment_date: '2026-11-20',
        members: [
          {
            full_name: 'Nguyễn Văn An',
            phone: '0912345678',
            service_name: 'Khám tổng quát',
            start_time: '09:00'
          }
        ]
      };
    }
    return null;
  });
  const handleDownloadICS = (res: BookingResult) => {
    const rawDate = res.appointment_date || new Date().toISOString().split("T")[0];
    const dateStr = rawDate.replace(/-/g, "");
    const firstTime = res.members[0]?.start_time || "09:00";
    const lastTime = res.members[res.members.length - 1]?.start_time || firstTime;
    const [h, m] = firstTime.split(":").map(Number);
    const [lh, lm] = lastTime.split(":").map(Number);
    let endH = lh, endM = lm + 30;
    if (res.members.length <= 1) {
      endM = m + 30;
    }
    if (endM >= 60) {
      endH += Math.floor(endM / 60);
      endM %= 60;
    }
    const pad = (n: number) => n < 10 ? "0" + n : "" + n;
    const dtStart = `${dateStr}T${pad(h)}${pad(m)}00`;
    const dtEnd = `${dateStr}T${pad(endH)}${pad(endM)}00`;
    const pnrDisplay = res.group_code ? `MS-${res.group_code}` : res.pnr_code;
    const memberListStr = res.members.map((mem, idx) => `${idx + 1}. ${mem.full_name} (${mem.service_name} - ${mem.start_time})`).join("\\n");
    const desc = `Khám răng tại Nha Khoa Minh Sinh.\\nMã đặt chỗ: ${pnrDisplay}\\nCơ sở: ${res.branch_name}\\nĐịa chỉ: ${res.branch_address}\\n\\nDanh sách khách khám:\\n${memberListStr}\\n\\n* Quý khách vui lòng đến trước 10 phút để được phục vụ chu đáo nhất.`;
    
    const ics = [
      "BEGIN:VCALENDAR",
      "VERSION:2.0",
      "PRODID:-//Minh Sinh Dental//VI",
      "CALSCALE:GREGORIAN",
      "METHOD:PUBLISH",
      "BEGIN:VTIMEZONE",
      "TZID:Asia/Ho_Chi_Minh",
      "X-LIC-LOCATION:Asia/Ho_Chi_Minh",
      "BEGIN:STANDARD",
      "TZOFFSETFROM:+0700",
      "TZOFFSETTO:+0700",
      "TZNAME:+07",
      "DTSTART:19700101T000000",
      "END:STANDARD",
      "END:VTIMEZONE",
      "BEGIN:VEVENT",
      `UID:minhsinh-${Date.now()}@minhsinhdental.com`,
      `DTSTART;TZID=Asia/Ho_Chi_Minh:${dtStart}`,
      `DTEND;TZID=Asia/Ho_Chi_Minh:${dtEnd}`,
      "SUMMARY:Khám răng tại Nha Khoa Minh Sinh",
      `LOCATION:${res.branch_address || ""}`,
      `DESCRIPTION:${desc}`,
      "STATUS:CONFIRMED",
      "BEGIN:VALARM",
      "TRIGGER:-PT60M",
      "ACTION:DISPLAY",
      "DESCRIPTION:Nhắc nhở lịch hẹn khám răng",
      "END:VALARM",
      "END:VEVENT",
      "END:VCALENDAR"
    ].join("\r\n");

    const blob = new Blob([ics], { type: "text/calendar;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.setAttribute("download", `Lich-Kham-Nha-Khoa-Minh-Sinh-${pnrDisplay}.ics`);
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleOpenGoogleCalendar = (res: BookingResult) => {
    const rawDate = res.appointment_date || new Date().toISOString().split("T")[0];
    const dateStr = rawDate.replace(/-/g, "");
    const firstTime = res.members[0]?.start_time || "09:00";
    const lastTime = res.members[res.members.length - 1]?.start_time || firstTime;
    const [h, m] = firstTime.split(":").map(Number);
    const [lh, lm] = lastTime.split(":").map(Number);
    let endH = lh, endM = lm + 30;
    if (res.members.length <= 1) endM = m + 30;
    if (endM >= 60) { endH += Math.floor(endM / 60); endM %= 60; }
    const pad = (n: number) => n < 10 ? "0" + n : "" + n;
    const dtStart = `${dateStr}T${pad(h)}${pad(m)}00`;
    const dtEnd = `${dateStr}T${pad(endH)}${pad(endM)}00`;
    const pnrDisplay = res.group_code ? `MS-${res.group_code}` : res.pnr_code;
    const memberListStr = res.members.map((mem, idx) => `${idx + 1}. ${mem.full_name} (${mem.service_name} - ${mem.start_time})`).join("\n");
    const desc = `Khám răng tại Nha Khoa Minh Sinh.\nMã đặt chỗ: ${pnrDisplay}\nCơ sở: ${res.branch_name}\nĐịa chỉ: ${res.branch_address}\n\nDanh sách khách khám:\n${memberListStr}\n\n* Quý khách vui lòng đến trước 10 phút để được phục vụ chu đáo nhất.`;
    
    const url = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${encodeURIComponent("Khám răng tại Nha Khoa Minh Sinh")}&dates=${dtStart}/${dtEnd}&ctz=Asia/Ho_Chi_Minh&details=${encodeURIComponent(desc)}&location=${encodeURIComponent(res.branch_address || "")}`;
    window.open(url, "_blank");
  };


  // Tổng số người trong đoàn (Người đặt chính + Thành viên)
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

  // Tìm Category ID từ Service ID
  const getCategoryIdForService = (serviceId: string): number => {
    for (const cat of categories) {
      if (cat.services?.some(s => s.service_id?.toString() === serviceId)) {
        return cat.category_id;
      }
      if (cat.category_id?.toString() === serviceId) {
        return cat.category_id;
      }
    }
    return categories[0]?.category_id || 1;
  };

  const getServiceName = (serviceId: string): string => {
    for (const cat of categories) {
      const found = cat.services?.find(s => s.service_id?.toString() === serviceId);
      if (found) return found.name;
    }
    return 'Dịch vụ nha khoa';
  };

  // --- THUẬT TOÁN TỰ ĐỘNG CHIA CA NỐI TIẾP (Smart Auto-Allocation) ---
  const autoAllocateSlots = (startSlotTime?: string) => {
    const startTime = startSlotTime || formData.selectedTime;
    const startIndex = availableSlots.findIndex(s => (
      s.time === startTime || 
      s.start_time === startTime || 
      (s.time && s.time.startsWith(startTime))
    ));
    
    if (startIndex === -1) {
      return;
    }

    let remainingToAllocate = [
      { type: 'leader', id: 'leader', name: formData.leaderName || 'Người đặt lịch' },
      ...formData.members.map(m => ({ type: 'member', id: m.id, name: m.full_name || 'Thành viên' }))
    ];

    const newAllocations: { id: string; time: string; type: string }[] = [];
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

    setAutoAllocationNotice(`Đã tự động chia ca nối tiếp cho ${totalGroupSize} khách khám bắt đầu từ ${startTime}.`);
    setTimeout(() => setAutoAllocationNotice(''), 6000);
  };

  const handleGlobalTimeSelect = (time: string) => {
    const slot = availableSlots.find(s => s.time === time || s.start_time === time);
    const seats = slot?.available_chairs ?? slot?.available_seats ?? 5;

    if (seats >= totalGroupSize) {
      setFormData(prev => ({
        ...prev,
        selectedTime: time,
        members: prev.members.map(m => ({ ...m, start_time: time }))
      }));
      setAutoAllocationNotice(`Cả đoàn (${totalGroupSize} người) đã được xếp vào khung giờ ${time}.`);
      setTimeout(() => setAutoAllocationNotice(''), 4000);
    } else {
      autoAllocateSlots(time);
    }
  };

  const getRemainingSeatsForSlot = (time: string, excludeMemberId?: string) => {
    const slot = availableSlots.find(s => s.time === time || s.start_time === time);
    if (!slot) return 5;
    
    const totalSeats = slot.available_chairs ?? slot.available_seats ?? 5;
    
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

  // --- XỬ LÝ NHẬP LIỆU & VALIDATION CHO NGƯỜI ĐẶT LỊCH ---
  const handleLeaderNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setFormData(prev => ({ ...prev, leaderName: val }));
    if (hasInvalidNameChars(val)) {
      setErrors(prev => ({ ...prev, leaderName: NAME_INVALID_WARNING }));
    } else if (errors.leaderName) {
      if (errors.leaderName === NAME_INVALID_WARNING || val.trim().length >= 2 || !val.trim()) {
        setErrors(prev => ({ ...prev, leaderName: undefined }));
      }
    }
  };

  const handleLeaderNameBlur = () => {
    const trimmed = formData.leaderName.trim();
    if (!trimmed) {
      setErrors(prev => ({ ...prev, leaderName: 'Vui lòng nhập họ và tên người đặt lịch' }));
    } else if (hasInvalidNameChars(formData.leaderName)) {
      setErrors(prev => ({ ...prev, leaderName: NAME_INVALID_WARNING }));
    } else if (trimmed.length < 2) {
      setErrors(prev => ({ ...prev, leaderName: 'Họ và tên tối thiểu 2 ký tự' }));
    } else {
      setErrors(prev => ({ ...prev, leaderName: undefined }));
    }
  };

  const handleLeaderPhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const sanitized = sanitizePhone(e.target.value);
    setFormData(prev => ({ ...prev, leaderPhone: sanitized }));
    if (sanitized.length >= 10) {
      setErrors(prev => ({ ...prev, leaderPhone: undefined }));
    }
  };

  const handleLeaderPhoneBlur = () => {
    const digits = formData.leaderPhone.replace(/\D/g, '');
    if (!digits) {
      setErrors(prev => ({ ...prev, leaderPhone: 'Vui lòng nhập số điện thoại' }));
    } else if (digits.length < 10) {
      setErrors(prev => ({ ...prev, leaderPhone: `Số điện thoại phải từ 10 đến 11 chữ số (hiện có ${digits.length} số)` }));
    } else {
      setErrors(prev => ({ ...prev, leaderPhone: undefined }));
    }
  };

  // --- QUẢN LÝ THÀNH VIÊN ĐI CÙNG ---
  const addMember = () => {
    if (formData.members.length >= 19) return;
    
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
        phone: '',
        service_id: defaultServiceId,
        start_time: prev.selectedTime
      }]
    }));
  };

  const removeMember = (id: string) => {
    setFormData(prev => ({ ...prev, members: prev.members.filter(m => m.id !== id) }));
    if (errors.members && errors.members[id]) {
      const updatedMembersErrors = { ...errors.members };
      delete updatedMembersErrors[id];
      setErrors(prev => ({ ...prev, members: updatedMembersErrors }));
    }
  };

  const handleMemberNameChange = (id: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      members: prev.members.map(m => m.id === id ? { ...m, full_name: value } : m)
    }));
    if (hasInvalidNameChars(value)) {
      setErrors(prev => ({
        ...prev,
        members: {
          ...prev.members,
          [id]: {
            ...prev.members?.[id],
            full_name: NAME_INVALID_WARNING
          }
        }
      }));
    } else if (errors.members?.[id]?.full_name) {
      setErrors(prev => {
        const memErr = { ...prev.members };
        if (memErr[id]) {
          const currentErr = memErr[id].full_name;
          if (currentErr === NAME_INVALID_WARNING || value.trim().length >= 2 || !value.trim()) {
            delete memErr[id].full_name;
          }
        }
        return { ...prev, members: memErr };
      });
    }
  };

  const handleMemberNameBlur = (id: string) => {
    const member = formData.members.find(m => m.id === id);
    if (!member) return;
    const trimmed = member.full_name.trim();
    if (!trimmed) {
      setErrors(prev => ({
        ...prev,
        members: {
          ...prev.members,
          [id]: {
            ...prev.members?.[id],
            full_name: 'Vui lòng nhập họ tên cho thành viên'
          }
        }
      }));
    } else if (hasInvalidNameChars(member.full_name)) {
      setErrors(prev => ({
        ...prev,
        members: {
          ...prev.members,
          [id]: {
            ...prev.members?.[id],
            full_name: NAME_INVALID_WARNING
          }
        }
      }));
    } else if (trimmed.length < 2) {
      setErrors(prev => ({
        ...prev,
        members: {
          ...prev.members,
          [id]: {
            ...prev.members?.[id],
            full_name: 'Họ và tên tối thiểu 2 ký tự'
          }
        }
      }));
    } else {
      setErrors(prev => {
        const memErr = { ...prev.members };
        if (memErr[id]) {
          delete memErr[id].full_name;
        }
        return { ...prev, members: memErr };
      });
    }
  };

  const handleMemberPhoneChange = (id: string, value: string) => {
    const sanitized = sanitizePhone(value);
    setFormData(prev => ({
      ...prev,
      members: prev.members.map(m => m.id === id ? { ...m, phone: sanitized } : m)
    }));
    if (sanitized.length >= 10 && errors.members?.[id]?.phone) {
      setErrors(prev => {
        const memErr = { ...prev.members };
        if (memErr[id]) {
          delete memErr[id].phone;
        }
        return { ...prev, members: memErr };
      });
    }
  };

  const handleMemberPhoneBlur = (id: string) => {
    const member = formData.members.find(m => m.id === id);
    if (!member || !member.phone) return;
    const digits = member.phone.replace(/\D/g, '');
    if (digits.length > 0 && digits.length < 10) {
      setErrors(prev => ({
        ...prev,
        members: {
          ...prev.members,
          [id]: {
            ...prev.members?.[id],
            phone: `Số điện thoại phải từ 10 đến 11 chữ số (hiện có ${digits.length} số)`
          }
        }
      }));
    } else {
      setErrors(prev => {
        const memErr = { ...prev.members };
        if (memErr[id]) {
          delete memErr[id].phone;
        }
        return { ...prev, members: memErr };
      });
    }
  };

  const updateMemberService = (id: string, serviceId: string) => {
    setFormData(prev => ({
      ...prev,
      members: prev.members.map(m => m.id === id ? { ...m, service_id: serviceId } : m)
    }));
  };

  const updateMemberTime = (id: string, time: string) => {
    setFormData(prev => ({
      ...prev,
      members: prev.members.map(m => m.id === id ? { ...m, start_time: time } : m)
    }));
  };

  // --- VALIDATE BƯỚC 2 TRƯỚC KHI TIẾP TỤC ---
  const validateStep2 = (): boolean => {
    const newErrors: typeof errors = { members: {} };
    let hasError = false;

    // Validate họ tên người đặt
    const trimmedLeaderName = formData.leaderName.trim();
    if (!trimmedLeaderName) {
      newErrors.leaderName = 'Vui lòng nhập họ và tên người đặt lịch';
      hasError = true;
    } else if (hasInvalidNameChars(formData.leaderName)) {
      newErrors.leaderName = NAME_INVALID_WARNING;
      hasError = true;
    } else if (trimmedLeaderName.length < 2) {
      newErrors.leaderName = 'Họ và tên tối thiểu 2 ký tự';
      hasError = true;
    }

    // Validate SĐT người đặt
    const cleanLeaderPhone = formData.leaderPhone.replace(/\D/g, '');
    if (!cleanLeaderPhone) {
      newErrors.leaderPhone = 'Vui lòng nhập số điện thoại';
      hasError = true;
    } else if (cleanLeaderPhone.length < 10) {
      newErrors.leaderPhone = `Số điện thoại phải từ 10 đến 11 chữ số (hiện có ${cleanLeaderPhone.length} số)`;
      hasError = true;
    }

    // Validate danh sách thành viên đi cùng
    formData.members.forEach((m, idx) => {
      const mErrors: { full_name?: string; phone?: string } = {};
      const mName = m.full_name.trim();
      if (!mName) {
        mErrors.full_name = `Vui lòng nhập họ tên cho thành viên ${idx + 1}`;
        hasError = true;
      } else if (hasInvalidNameChars(m.full_name)) {
        mErrors.full_name = NAME_INVALID_WARNING;
        hasError = true;
      } else if (mName.length < 2) {
        mErrors.full_name = 'Họ và tên tối thiểu 2 ký tự';
        hasError = true;
      }

      if (m.phone && m.phone.trim().length > 0) {
        const mCleanPhone = m.phone.replace(/\D/g, '');
        if (mCleanPhone.length < 10) {
          mErrors.phone = `Số điện thoại phải từ 10 đến 11 chữ số (hiện có ${mCleanPhone.length} số)`;
          hasError = true;
        }
      }

      if (Object.keys(mErrors).length > 0 && newErrors.members) {
        newErrors.members[m.id] = mErrors;
      }
    });

    setErrors(newErrors);
    return !hasError;
  };

  const handleProceedToStep3 = () => {
    if (validateStep2()) {
      setStep(3);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // --- SUBMIT VÀ XÁC NHẬN ĐẶT LỊCH ---
  const handleSubmitBooking = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (formData.honeypot) return;

    if (!validateStep2()) {
      setStep(2);
      window.scrollTo({ top: 0, behavior: 'smooth' });
      return;
    }

    const warnings = calculateCapacityWarnings();
    if (warnings.length > 0) {
      setErrors(prev => ({
        ...prev,
        submit: 'Không thể đặt lịch: Có khung giờ vượt quá số ghế trống. Vui lòng bấm "Tự động chia ca tối ưu" hoặc chọn lại giờ!'
      }));
      return;
    }

    setLoading(true);
    setErrors(prev => ({ ...prev, submit: undefined }));

    try {
      const leaderCatId = getCategoryIdForService(formData.leaderServiceId);
      const leaderPhoneClean = formData.leaderPhone.replace(/\D/g, '');

      // Payload cấu trúc đầy đủ chuẩn backend Django BookingCreateView:
      // clinic_id, date, start_time, patients (fullName, phone, start_time, category_id)
      const patients = [
        {
          fullName: formData.leaderName.trim(),
          phone: leaderPhoneClean,
          email: '',
          start_time: formData.selectedTime,
          category_id: leaderCatId
        },
        ...formData.members.map(m => {
          const mPhoneClean = m.phone ? m.phone.replace(/\D/g, '') : '';
          return {
            fullName: m.full_name.trim(),
            // Fallback số điện thoại của người đặt nếu thành viên không có số riêng
            phone: mPhoneClean.length >= 10 ? mPhoneClean : leaderPhoneClean,
            email: '',
            start_time: m.start_time || formData.selectedTime,
            category_id: getCategoryIdForService(m.service_id)
          };
        })
      ];

      const payload = {
        clinic_id: parseInt(formData.clinicId, 10),
        date: formData.date,
        start_time: formData.selectedTime,
        patients: patients,
        // Backward compatibility
        appointment_date: formData.date,
        leader_name: formData.leaderName.trim(),
        leader_phone: leaderPhoneClean,
        leader_service_id: parseInt(formData.leaderServiceId, 10) || 1,
        leader_start_time: formData.selectedTime,
        members: formData.members.map(m => {
          const mPhoneClean = m.phone ? m.phone.replace(/\D/g, '') : '';
          return {
            full_name: m.full_name.trim(),
            phone: mPhoneClean.length >= 10 ? mPhoneClean : leaderPhoneClean,
            service_id: parseInt(m.service_id, 10) || 1,
            start_time: m.start_time || formData.selectedTime
          };
        })
      };

      const res = await fetch('/api/bookings/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      const data = await res.json().catch(() => ({}));

      if (res.ok || res.status === 201 || res.status === 200) {
        setBookingResult({
          pnr_code: data.pnr_code || 'MS-SUCCESS',
          group_code: data.group_code || 'GRP-01',
          clinic_name: clinics.find(c => (c.clinic_id ?? c.id)?.toString() === formData.clinicId)?.name || 'Nha Khoa Minh Sinh',
          clinic_address: clinics.find(c => (c.clinic_id ?? c.id)?.toString() === formData.clinicId)?.address || '',
          appointment_date: formData.date,
          members: [
            {
              full_name: formData.leaderName.trim(),
              phone: leaderPhoneClean,
              service_name: getServiceName(formData.leaderServiceId),
              start_time: formData.selectedTime
            },
            ...formData.members.map(m => {
              const mClean = m.phone ? m.phone.replace(/\D/g, '') : '';
              return {
                full_name: m.full_name.trim(),
                phone: mClean.length >= 10 ? mClean : leaderPhoneClean,
                service_name: getServiceName(m.service_id),
                start_time: m.start_time || formData.selectedTime
              };
            })
          ]
        });
        setStep(4);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        const errorMsg = data.error || data.warning || data.message || 'Có lỗi xảy ra khi tạo đơn đặt lịch. Vui lòng kiểm tra lại thông tin!';
        setErrors(prev => ({ ...prev, submit: errorMsg }));
      }
    } catch (err: any) {
      console.error('Lỗi khi gửi yêu cầu đặt lịch:', err);
      setErrors(prev => ({ ...prev, submit: 'Không thể kết nối đến máy chủ. Vui lòng thử lại sau giây lát!' }));
    } finally {
      setLoading(false);
    }
  };

  const renderServiceSelect = (value: string, onChange: (e: React.ChangeEvent<HTMLSelectElement>) => void) => (
    <select
      className="w-full px-3.5 py-2.5 sm:px-4 sm:py-3 border border-gray-300 rounded-[10px] focus:ring-2 focus:ring-blue-500 bg-white text-gray-800 text-xs sm:text-sm font-medium outline-none transition-all"
      value={value}
      onChange={onChange}
      required
    >
      <option value="">-- Chọn dịch vụ khám --</option>
      {categories.map(cat => (
        <optgroup key={cat.category_id} label={`${cat.name}`}>
          {cat.services.map(s => (
            <option key={s.service_id} value={s.service_id.toString()}>
              {s.name} ({cat.estimate_time || 30} phút)
            </option>
          ))}
        </optgroup>
      ))}
    </select>
  );

  const capacityWarnings = calculateCapacityWarnings();
  const perfectSlots = availableSlots.filter(s => (s.available_chairs ?? s.available_seats ?? 0) >= totalGroupSize);

  return (
    <div className="w-full max-w-7xl mx-auto p-3.5 sm:p-6 md:p-8 lg:p-10 bg-white rounded-[10px] shadow-xl sm:shadow-2xl border border-gray-100 overflow-x-hidden">
      <input
        type="text"
        value={formData.honeypot}
        onChange={e => setFormData({ ...formData, honeypot: e.target.value })}
        className="hidden"
        tabIndex={-1}
        autoComplete="off"
      />

      {/* Stepper (Bước 1 - 2 - 3) */}
      {step < 4 && (
        <div className="max-w-xl mx-auto flex items-center justify-between mb-8 sm:mb-10 relative px-2">
          <div className="absolute top-1/2 left-4 right-4 h-0.5 bg-gray-200 -translate-y-1/2 z-0" />
          {[1, 2, 3].map((s) => (
            <div key={s} className={`relative z-10 flex flex-col items-center gap-1.5 ${step >= s ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 sm:w-10 sm:h-10 rounded-full flex items-center justify-center font-bold text-xs sm:text-sm transition-all duration-300 ${
                step >= s ? 'bg-blue-600 text-white shadow-md shadow-blue-200 scale-105' : 'bg-gray-100 text-gray-500 border border-gray-300'
              }`}>
                {step > s ? <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5" /> : s}
              </div>
              <span className="text-[11px] sm:text-xs font-bold uppercase tracking-tight">
                {s === 1 ? 'Cơ sở & Ngày' : s === 2 ? 'Người khám' : 'Giờ khám'}
              </span>
            </div>
          ))}
        </div>
      )}

      <AnimatePresence mode="wait">
        {/* STEP 1: CLINIC & DATE */}
        {step === 1 && (
          <motion.div
            key="step1"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-6"
          >
            <div className="bg-blue-50/70 p-4 sm:p-6 md:p-8 rounded-[10px] border border-blue-100 space-y-4">
              <h2 className="text-lg sm:text-xl font-black text-blue-900 flex items-center gap-2">
                <Calendar className="w-5 h-5 text-blue-600 shrink-0" /> Chọn Địa Điểm & Ngày Hẹn Khám
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                <div className="space-y-1.5">
                  <label className="text-xs sm:text-sm font-bold text-gray-700">Cơ sở Nha Khoa</label>
                  <select
                    className="w-full px-3.5 py-3 rounded-[10px] border-2 border-gray-200 focus:border-blue-500 bg-white text-gray-800 text-sm outline-none transition-all"
                    value={formData.clinicId}
                    onChange={e => setFormData({ ...formData, clinicId: e.target.value })}
                  >
                    {clinics.map(c => (
                      <option key={c.clinic_id ?? c.id} value={(c.clinic_id ?? c.id)?.toString()}>
                        {c.name} {c.address ? `- ${c.address}` : ''}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div className="space-y-1.5">
                  <label className="text-xs sm:text-sm font-bold text-gray-700">Ngày hẹn khám</label>
                  <input
                    type="date"
                    min={new Date().toISOString().split('T')[0]}
                    className="w-full px-3.5 py-3 rounded-[10px] border-2 border-gray-200 focus:border-blue-500 bg-white text-gray-800 text-sm outline-none transition-all"
                    value={formData.date}
                    onChange={e => setFormData({ ...formData, date: e.target.value })}
                  />
                </div>
              </div>
            </div>

            <div className="flex justify-end pt-2">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="w-full sm:w-auto bg-blue-600 text-white px-8 py-3.5 sm:py-4 rounded-[10px] font-bold hover:bg-blue-700 transition-all flex items-center justify-center gap-2 shadow-lg shadow-blue-200 text-sm sm:text-base active:scale-95"
              >
                Tiếp tục: Nhập thông tin người khám <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 2: MEMBERS & CONTACT INFO */}
        {step === 2 && (
          <motion.div
            key="step2"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            {/* Header thông tin người khám */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-2 border-b border-gray-100">
              <div>
                <h2 className="text-xl sm:text-2xl font-black text-gray-800">Thông tin người khám</h2>
                <p className="text-xs sm:text-sm text-gray-500 mt-0.5">Vui lòng điền thông tin người liên hệ chính và người đi cùng (nếu có)</p>
              </div>
              <div className="self-start sm:self-auto bg-amber-50 text-amber-800 px-3.5 py-1.5 rounded-full text-xs font-bold border border-amber-200 flex items-center gap-1.5 shadow-sm">
                <Sparkles className="w-3.5 h-3.5 text-amber-600 shrink-0" />
                <span>Hỗ trợ đặt nhóm lên tới 20 người</span>
              </div>
            </div>

            {/* Khung người liên hệ chính (Trưởng nhóm) */}
            <div className="bg-white border-2 border-blue-200 rounded-[10px] p-4 sm:p-6 space-y-4 shadow-sm">
              <div className="flex items-center gap-2 text-blue-700 font-bold text-xs sm:text-sm uppercase tracking-wider">
                <User className="w-4 h-4" /> Người đặt lịch & liên hệ chính
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-xs font-bold text-gray-700">Họ và tên *</label>
                  <input
                    type="text"
                    placeholder="Ví dụ: Nguyễn Văn A"
                    className={`w-full px-3.5 py-2.5 sm:px-4 sm:py-3 rounded-[10px] border text-sm outline-none transition-all ${
                      errors.leaderName ? 'border-red-500 ring-1 ring-red-200' : 'border-gray-200 focus:ring-2 focus:ring-blue-500'
                    }`}
                    value={formData.leaderName}
                    onChange={handleLeaderNameChange}
                    onBlur={handleLeaderNameBlur}
                  />
                  {errors.leaderName && (
                    <p className="text-[11px] text-red-500 font-medium flex items-center gap-1 mt-1">
                      <AlertCircle className="w-3 h-3 flex-shrink-0" /> {errors.leaderName}
                    </p>
                  )}
                  <p className="text-[11px] text-gray-400">Chỉ cho phép chữ cái tiếng Việt và khoảng trắng</p>
                </div>

                <div className="space-y-1">
                  <label className="text-xs font-bold text-gray-700">Số điện thoại liên hệ *</label>
                  <input
                    type="tel"
                    placeholder="Ví dụ: 0912345678"
                    maxLength={11}
                    className={`w-full px-3.5 py-2.5 sm:px-4 sm:py-3 rounded-[10px] border text-sm outline-none transition-all ${
                      errors.leaderPhone ? 'border-red-500 ring-2 ring-red-100' : 'border-gray-200 focus:ring-2 focus:ring-blue-500'
                    }`}
                    value={formData.leaderPhone}
                    onChange={handleLeaderPhoneChange}
                    onBlur={handleLeaderPhoneBlur}
                  />
                  {errors.leaderPhone && (
                    <p className="text-xs text-red-500 font-medium flex items-center gap-1 mt-1">
                      <AlertCircle className="w-3.5 h-3.5" /> {errors.leaderPhone}
                    </p>
                  )}
                  <p className="text-[11px] text-gray-400">Chỉ nhận chữ số (từ 10 đến 11 số)</p>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold text-gray-700">Dịch vụ nha khoa mong muốn *</label>
                {renderServiceSelect(formData.leaderServiceId, e => setFormData({ ...formData, leaderServiceId: e.target.value }))}
              </div>
            </div>

            {/* Khung thành viên đi cùng */}
            <div className="space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-2">
                  <h3 className="font-bold text-gray-800 text-sm sm:text-base">
                    Thành viên đi cùng ({formData.members.length})
                  </h3>
                  <span className="text-xs text-gray-500 font-normal">(tùy chọn)</span>
                </div>
                
                <button
                  type="button"
                  onClick={addMember}
                  className="w-full sm:w-auto flex items-center justify-center gap-2 bg-green-50 text-green-700 px-4 py-2.5 sm:py-2 rounded-[10px] font-bold hover:bg-green-100 transition-all border border-green-200 text-xs sm:text-sm active:scale-95"
                >
                  <Plus className="w-4 h-4" /> Thêm người đi cùng
                </button>
              </div>

              {formData.members.length === 0 && (
                <div className="text-center py-6 border-2 border-dashed border-gray-200 rounded-[10px] bg-gray-50/50">
                  <p className="text-xs sm:text-sm text-gray-500 font-medium">Chưa có người đi cùng. Bấm &quot;Thêm người đi cùng&quot; nếu bạn đi theo nhóm hoặc gia đình.</p>
                </div>
              )}

              <div className="space-y-3">
                {formData.members.map((m, idx) => {
                  const mErrors = errors.members?.[m.id];
                  return (
                    <motion.div
                      layout
                      key={m.id}
                      className="bg-gray-50/90 p-3.5 sm:p-4 rounded-[10px] border border-gray-200 space-y-3"
                    >
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-black text-gray-600 bg-white px-2.5 py-1 rounded-lg border border-gray-200">
                          Thành viên #{idx + 1}
                        </span>
                        <button
                          type="button"
                          onClick={() => removeMember(m.id)}
                          className="text-red-500 hover:text-red-700 transition-colors p-1.5 rounded-lg hover:bg-red-50 flex items-center gap-1 text-xs font-medium"
                          title="Xóa thành viên"
                        >
                          <Trash2 className="w-4 h-4" /> <span className="hidden sm:inline">Xóa</span>
                        </button>
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div className="space-y-1">
                          <label className="text-[11px] font-bold text-gray-700">Họ và tên *</label>
                          <input
                            type="text"
                            placeholder={`Họ và tên thành viên ${idx + 1}`}
                            className={`w-full px-3 py-2 rounded-[10px] border text-xs sm:text-sm bg-white outline-none transition-all ${
                              mErrors?.full_name ? 'border-red-500 ring-1 ring-red-200' : 'border-gray-200 focus:ring-2 focus:ring-blue-500'
                            }`}
                            value={m.full_name}
                            onChange={e => handleMemberNameChange(m.id, e.target.value)}
                            onBlur={() => handleMemberNameBlur(m.id)}
                          />
                          {mErrors?.full_name && (
                            <p className="text-[11px] text-red-500 font-medium flex items-center gap-1 mt-0.5">
                              <AlertCircle className="w-3 h-3 flex-shrink-0" /> {mErrors.full_name}
                            </p>
                          )}
                        </div>

                        <div className="space-y-1">
                          <label className="text-[11px] font-bold text-gray-700">
                            Số điện thoại riêng <span className="font-normal text-gray-400">(nếu có)</span>
                          </label>
                          <input
                            type="tel"
                            placeholder="Dùng SĐT người đặt nếu để trống"
                            maxLength={11}
                            className={`w-full px-3 py-2 rounded-[10px] border text-xs sm:text-sm bg-white outline-none transition-all ${
                              mErrors?.phone ? 'border-red-500 ring-2 ring-red-100' : 'border-gray-200 focus:ring-2 focus:ring-blue-500'
                            }`}
                            value={m.phone}
                            onChange={e => handleMemberPhoneChange(m.id, e.target.value)}
                            onBlur={() => handleMemberPhoneBlur(m.id)}
                          />
                          {mErrors?.phone && (
                            <p className="text-[11px] text-red-500 font-medium flex items-center gap-1 mt-0.5">
                              <AlertCircle className="w-3 h-3" /> {mErrors.phone}
                            </p>
                          )}
                        </div>
                      </div>

                      <div className="space-y-1">
                        <label className="text-[11px] font-bold text-gray-700">Dịch vụ cho thành viên *</label>
                        {renderServiceSelect(m.service_id, e => updateMemberService(m.id, e.target.value))}
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </div>

            {/* Nút điều hướng Step 2 */}
            <div className="flex flex-col-reverse sm:flex-row justify-between gap-3 pt-6 border-t border-gray-100">
              <button
                type="button"
                onClick={() => setStep(1)}
                className="w-full sm:w-auto px-6 py-3.5 text-gray-600 font-bold hover:bg-gray-100 rounded-[10px] transition-all text-sm flex items-center justify-center gap-1.5"
              >
                <ChevronLeft className="w-4 h-4" /> Quay lại
              </button>
              
              <button
                type="button"
                onClick={handleProceedToStep3}
                className="w-full sm:w-auto bg-blue-600 text-white px-8 py-3.5 sm:py-4 rounded-[10px] font-bold hover:bg-blue-700 transition-all shadow-lg shadow-blue-200 text-sm sm:text-base flex items-center justify-center gap-2 active:scale-95"
              >
                Tiếp tục: Chọn giờ khám <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 3: TIME SELECTION & CONFIRMATION */}
        {step === 3 && (
          <motion.div
            key="step3"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            className="space-y-6"
          >
            <div className="flex flex-col gap-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pb-2 border-b border-gray-100">
                <div>
                  <h2 className="text-xl sm:text-2xl font-black text-gray-800">Chọn giờ khám thông minh</h2>
                  <p className="text-xs sm:text-sm text-gray-500">Đoàn của bạn gồm {totalGroupSize} người. Hệ thống tự động kiểm tra số ghế trống theo thời gian thực.</p>
                </div>
              </div>
              
              {/* Gợi ý khung giờ còn đủ chỗ cho cả đoàn */}
              {perfectSlots.length > 0 && (
                <div className="bg-green-50 border border-green-200 p-3.5 sm:p-4 rounded-[10px]">
                  <p className="text-xs sm:text-sm font-bold text-green-900 mb-2 flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4 text-green-600 shrink-0" /> Khung giờ còn đủ ghế cho cả đoàn ({totalGroupSize} người):
                  </p>
                  <div className="flex flex-wrap gap-1.5 sm:gap-2">
                    {perfectSlots.slice(0, 6).map(s => {
                      const t = s.time || s.start_time || '';
                      return (
                        <button
                          key={t}
                          type="button"
                          onClick={() => handleGlobalTimeSelect(t)}
                          className="px-3 py-1.5 bg-white border border-green-300 text-green-800 rounded-lg text-xs font-bold hover:bg-green-600 hover:text-white transition-all shadow-sm active:scale-95"
                        >
                          {t}
                        </button>
                      );
                    })}
                  </div>
                </div>
              )}

              {autoAllocationNotice && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="bg-blue-50 border border-blue-200 text-blue-900 p-3.5 sm:p-4 rounded-[10px] text-xs sm:text-sm font-bold flex items-center gap-2.5 shadow-sm"
                >
                  <Zap className="w-4 h-4 text-blue-600 fill-blue-600 shrink-0" />
                  <span>{autoAllocationNotice}</span>
                </motion.div>
              )}
            </div>

            {/* Time Grid (Lưới giờ chọn bắt đầu) */}
            <div className="space-y-3">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <label className="text-xs font-black text-gray-700 uppercase tracking-wider">
                  Giờ bắt đầu cho đoàn:
                </label>
                <button
                  type="button"
                  onClick={() => autoAllocateSlots()}
                  className="self-start sm:self-auto text-xs bg-blue-50 text-blue-700 px-3 py-1.5 rounded-lg font-bold border border-blue-200 flex items-center gap-1 hover:bg-blue-600 hover:text-white transition-all shadow-sm active:scale-95"
                >
                  <Zap className="w-3.5 h-3.5" /> Tự động chia ca tối ưu
                </button>
              </div>

              <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-8 gap-1.5 sm:gap-2">
                {TIME_STEPS.map(time => {
                  const slot = availableSlots.find(s => s.time === time || s.start_time === time);
                  const seats = slot?.available_chairs ?? slot?.available_seats ?? 0;
                  const isFull = seats <= 0;
                  const isSelected = formData.selectedTime === time;

                  return (
                    <button
                      key={time}
                      type="button"
                      disabled={isFull}
                      onClick={() => handleGlobalTimeSelect(time)}
                      className={`relative p-2.5 sm:p-3 rounded-[10px] border-2 transition-all flex flex-col items-center justify-center gap-0.5 ${
                        isSelected
                          ? 'bg-blue-600 text-white font-bold ring-2 ring-blue-600 shadow-md transform scale-105 transition-all border-blue-600'
                          : isFull
                          ? 'bg-gray-50 border-gray-100 opacity-40 cursor-not-allowed'
                          : 'border-gray-200 bg-white hover:border-blue-300'
                      }`}
                    >
                      <span className={`text-xs sm:text-sm font-bold ${isSelected ? 'text-white font-bold' : 'text-gray-800'}`}>
                        {time}
                      </span>
                      <span className={`text-[10px] font-medium ${isSelected ? 'text-blue-100 font-medium' : isFull ? 'text-gray-400' : seats < 3 ? 'text-red-500 font-bold' : 'text-gray-500'}`}>
                        {isFull ? 'Hết chỗ' : `${seats} ghế`}
                      </span>
                      {isSelected && (
                        <div className="absolute -top-1.5 -right-1.5 bg-white text-blue-600 rounded-full p-0.5 shadow-sm">
                          <CheckCircle2 className="w-3.5 h-3.5" />
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Lịch trình chi tiết từng thành viên */}
            <div className="bg-white rounded-[10px] p-4 sm:p-6 text-slate-800 shadow-sm border border-blue-200 space-y-4">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 pb-3 border-b border-blue-100">
                <h3 className="text-sm sm:text-base font-bold flex items-center gap-2 text-blue-900">
                  <ListOrdered className="w-4 h-4 text-blue-600" /> Lịch trình chi tiết từng khách
                </h3>
                <span className="text-xs text-slate-500">Có thể chỉnh giờ riêng cho từng thành viên bên dưới</span>
              </div>
              
              <div className="space-y-2.5">
                {/* Dòng Người đặt lịch */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-blue-50/70 p-3 sm:p-3.5 rounded-[10px] border border-blue-100 shadow-sm">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-xs shrink-0 shadow-sm">
                      NLH
                    </div>
                    <div>
                      <div className="text-xs sm:text-sm font-bold text-slate-900">{formData.leaderName || 'Người đặt lịch'}</div>
                      <div className="text-[10px] text-blue-700 font-bold uppercase tracking-wider">{getServiceName(formData.leaderServiceId)}</div>
                    </div>
                  </div>

                  <select
                    className="w-full sm:w-auto bg-white border border-blue-200 text-slate-800 rounded-[10px] px-3 py-2 text-xs font-bold outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 shadow-sm"
                    value={formData.selectedTime}
                    onChange={e => setFormData({ ...formData, selectedTime: e.target.value })}
                  >
                    {TIME_STEPS.map(t => {
                      const rem = getRemainingSeatsForSlot(t);
                      return <option key={t} value={t} disabled={rem <= 0}>{t} ({rem} chỗ trống)</option>;
                    })}
                  </select>
                </div>

                {/* Các dòng Thành viên đi cùng */}
                {formData.members.map((m, idx) => (
                  <div
                    key={m.id}
                    className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-slate-50 p-3 sm:p-3.5 rounded-[10px] border border-slate-200/80 shadow-sm"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-8 h-8 sm:w-9 sm:h-9 rounded-full bg-slate-200 text-slate-700 flex items-center justify-center font-bold text-xs shrink-0 shadow-sm">
                        {idx + 1}
                      </div>
                      <div>
                        <div className="text-xs sm:text-sm font-bold text-slate-900">{m.full_name || `Thành viên ${idx + 1}`}</div>
                        <div className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider">{getServiceName(m.service_id)}</div>
                      </div>
                    </div>

                    <select
                      className="w-full sm:w-auto bg-white border border-slate-200 text-slate-800 rounded-[10px] px-3 py-2 text-xs font-bold outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 shadow-sm"
                      value={m.start_time}
                      onChange={e => updateMemberTime(m.id, e.target.value)}
                    >
                      {TIME_STEPS.map(t => {
                        const rem = getRemainingSeatsForSlot(t, m.id);
                        return <option key={t} value={t} disabled={rem <= 0}>{t} ({rem} chỗ trống)</option>;
                      })}
                    </select>
                  </div>
                ))}
              </div>
            </div>

            {/* Cảnh báo quá tải nếu có */}
            {capacityWarnings.length > 0 && (
              <div className="p-4 bg-red-50 border-2 border-red-200 rounded-[10px] space-y-2">
                <div className="flex items-center gap-2 text-red-700 font-black text-xs sm:text-sm">
                  <AlertTriangle className="w-5 h-5 shrink-0" /> CẢNH BÁO: KHUNG GIỜ VƯỢT QUÁ SỨC CHỨA
                </div>
                {capacityWarnings.map((w, i) => (
                  <p key={i} className="text-xs text-red-600 font-medium pl-6">• {w}</p>
                ))}
                <button
                  type="button"
                  onClick={() => autoAllocateSlots()}
                  className="w-full mt-2 py-2.5 bg-red-600 text-white rounded-[10px] text-xs font-bold hover:bg-red-700 transition-all shadow-sm active:scale-98"
                >
                  Bấm vào đây để tự động chia ca tối ưu ngay
                </button>
              </div>
            )}

            {/* Hiển thị lỗi submit nếu có */}
            {errors.submit && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-[10px] text-xs sm:text-sm text-red-700 font-bold flex items-center gap-2">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{errors.submit}</span>
              </div>
            )}

            {/* Nút hành động Bước 3 */}
            <div className="flex flex-col-reverse sm:flex-row justify-between gap-3 pt-6 border-t border-gray-100">
              <button
                type="button"
                onClick={() => setStep(2)}
                className="w-full sm:w-auto px-6 py-3.5 text-gray-600 font-bold hover:bg-gray-100 rounded-[10px] transition-all text-sm flex items-center justify-center gap-1.5"
              >
                <ChevronLeft className="w-4 h-4" /> Quay lại sửa thông tin
              </button>

              <button
                type="button"
                disabled={loading || capacityWarnings.length > 0}
                onClick={handleSubmitBooking}
                className="w-full sm:w-auto bg-blue-600 text-white px-8 sm:px-10 py-3.5 sm:py-4 rounded-[10px] font-bold hover:bg-blue-700 transition-all shadow-xl shadow-blue-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm sm:text-base active:scale-95"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    <span>Đang gửi đơn đặt lịch...</span>
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-5 h-5" />
                    <span>Xác nhận Đặt lịch khám</span>
                  </>
                )}
              </button>
            </div>
          </motion.div>
        )}

        {/* STEP 4: BOARDING PASS (HOÀN TẤT) */}
        {step === 4 && bookingResult && (
          <motion.div
            key="step4"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="w-full max-w-3xl mx-auto space-y-6 sm:space-y-8"
          >
            <div className="text-center space-y-2">
              <div className="w-16 h-16 sm:w-20 sm:h-20 bg-green-100 text-green-600 rounded-full flex items-center justify-center mx-auto mb-3 shadow-inner">
                <CheckCircle2 className="w-8 h-8 sm:w-10 sm:h-10" />
              </div>
              <h2 className="text-2xl sm:text-3xl font-black text-gray-900">Đặt lịch thành công!</h2>
              <p className="text-xs sm:text-sm text-gray-500 font-medium">
                Vui lòng lưu lại Thẻ tiếp nhận (Boarding Pass) bên dưới để làm thủ tục nhanh tại quầy lễ tân.
              </p>
            </div>

            {/* Thẻ E-Boarding Pass */}
            <div className="relative group">
              <div className="bg-gradient-to-br from-indigo-950 via-blue-900 to-blue-800 text-white rounded-[10px] overflow-hidden shadow-2xl border border-blue-700 p-5 sm:p-8 space-y-6 sm:space-y-8">
                {/* Header vé */}
                <div className="flex justify-between items-start border-b border-white/15 pb-4 sm:pb-6">
                  <div>
                    <div className="text-[10px] font-black uppercase tracking-[0.25em] text-blue-300 mb-1">
                      Minh Sinh Dental Clinic
                    </div>
                    <h3 className="text-xl sm:text-2xl font-black tracking-tight">E-BOARDING PASS</h3>
                  </div>
                  <div className="text-right">
                    <div className="text-[10px] font-bold text-blue-300 uppercase mb-0.5">Mã đặt chỗ (PNR)</div>
                    <div className="text-2xl sm:text-3xl font-mono font-black text-amber-400">
                      {formatPNR(bookingResult.pnr_code)}
                    </div>
                  </div>
                </div>

                {/* Thông tin cơ sở & ngày */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 sm:gap-6">
                  <div className="space-y-1">
                    <div className="text-[10px] font-bold text-blue-300 uppercase">Cơ sở khám</div>
                    <div className="font-black text-sm">{bookingResult.clinic_name}</div>
                  </div>
                  <div className="space-y-1">
                    <div className="text-[10px] font-bold text-blue-300 uppercase">Ngày hẹn</div>
                    <div className="font-black text-sm">{bookingResult.appointment_date}</div>
                  </div>
                  <div className="space-y-1 sm:col-span-1">
                    <div className="text-[10px] font-bold text-blue-300 uppercase">Địa chỉ</div>
                    <div className="font-medium text-xs leading-snug text-blue-100">{bookingResult.clinic_address}</div>
                  </div>
                </div>

                {/* Danh sách thành viên trong vé */}
                <div className="space-y-3">
                  <div className="text-[10px] font-black text-blue-300 uppercase tracking-widest">
                    Danh sách khách khám & Khung giờ ({bookingResult.members.length} người)
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    {bookingResult.members.map((m, i) => (
                      <div
                        key={i}
                        className="flex items-center justify-between bg-white/10 p-3 rounded-[10px] backdrop-blur-md border border-white/10"
                      >
                        <div className="space-y-0.5">
                          <div className="text-xs sm:text-sm font-black flex items-center gap-2">
                            <span>{m.full_name}</span>
                            {m.phone && <span className="text-[11px] font-normal text-blue-200">({m.phone})</span>}
                          </div>
                          <div className="text-[10px] text-blue-200">{m.service_name}</div>
                        </div>
                        <div className="text-right">
                          <div className="text-xs font-mono font-black text-amber-300 bg-amber-400/15 px-2.5 py-1 rounded-lg border border-amber-400/25">
                            {m.start_time}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Barcode & QR footer */}
                <div className="pt-4 sm:pt-6 border-t border-white/15 flex items-center justify-between gap-4">
                  <div className="flex items-center gap-2 sm:gap-3 opacity-70 overflow-hidden">
                    <Barcode className="w-8 h-8 sm:w-12 sm:h-12 shrink-0" />
                    <div className="font-mono text-[10px] sm:text-xs tracking-wider truncate">
                      MS-{bookingResult.group_code}
                    </div>
                  </div>
                  <div className="bg-white p-1.5 sm:p-2 rounded-[10px] shrink-0">
                    <QrCode className="w-8 h-8 sm:w-10 sm:h-10 text-blue-900" />
                  </div>
                </div>
              </div>
            </div>

            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-4">
              <button
                onClick={() => bookingResult && handleDownloadICS(bookingResult)}
                className="flex items-center justify-center gap-2 px-4 py-3 bg-blue-50 text-blue-700 rounded-[10px] hover:bg-blue-100 transition-colors font-medium"
              >
                <CalendarPlus className="w-5 h-5" />
                Thêm vào lịch
              </button>
              <button
                onClick={() => bookingResult && handleOpenGoogleCalendar(bookingResult)}
                className="flex items-center justify-center gap-2 px-4 py-3 bg-red-50 text-red-700 rounded-[10px] hover:bg-red-100 transition-colors font-medium"
              >
                <CalendarPlus className="w-5 h-5" />
                Google Calendar
              </button>
            </div>
            {/* Các nút in & đặt lịch mới */}
            <div className="flex flex-col sm:flex-row justify-center gap-3 pt-2">
              <button
                type="button"
                onClick={() => window.print()}
                className="w-full sm:w-1/2 px-6 py-3.5 bg-gray-100 text-gray-800 font-bold rounded-[10px] hover:bg-gray-200 transition-all flex items-center justify-center gap-2 text-sm shadow-sm active:scale-95"
              >
                <Printer className="w-4 h-4" /> In vé điện tử
              </button>
              <button
                type="button"
                onClick={() => window.location.reload()}
                className="w-full sm:w-1/2 px-6 py-3.5 bg-blue-600 text-white font-bold rounded-[10px] hover:bg-blue-700 transition-all flex items-center justify-center gap-2 text-sm shadow-lg shadow-blue-200 active:scale-95"
              >
                <PlaneTakeoff className="w-4 h-4" /> Đặt lịch hẹn mới
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
