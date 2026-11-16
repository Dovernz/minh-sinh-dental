"use client";

import React, { useEffect, useState, useRef } from "react";
import { useParams, useRouter } from "next/navigation";
import { 
  CheckCircle2, 
  Printer, 
  Home, 
  Download, 
  PlaneTakeoff, 
  MapPin, 
  Calendar, 
  Clock, 
  User, 
  Stethoscope,
  QrCode,
  ChevronRight
} from "lucide-react";
import { motion } from "framer-motion";

// --- Interfaces ---
interface Passenger {
  id: number;
  full_name: string;
  service_name: string;
  price: number;
  appointment_time: string;
  status: string;
}

interface BookingData {
  pnr: string;
  clinic_name: string;
  clinic_address: string;
  appointment_date: string;
  passengers: Passenger[];
  total_amount: number;
}

// --- Helper Functions ---
const formatPNR = (code: string): string => {
  if (!code) return "MSXXXX";
  // Nếu là mã group MS-GRP-..., lấy phần cuối hoặc hash, nhưng chuẩn hóa về 6 ký tự
  const clean = code.replace(/[^a-zA-Z0-9]/g, "");
  return clean.slice(-6).toUpperCase();
};

const formatCurrency = (amount: number) => {
  return new Intl.NumberFormat("vi-VN", {
    style: "currency",
    currency: "VND",
  }).format(amount);
};

export default function BookingSuccessPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [loading, setLoading] = useState(true);
  const [bookingData, setBookingData] = useState<BookingData | null>(null);
  const ticketRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchBookingDetails = async () => {
      try {
        setLoading(true);
        // Logic nhận diện API endpoint
        const isGroup = id.includes("-") || isNaN(Number(id));
        const endpoint = isGroup 
          ? `/api/bookings/group/${id}/` 
          : `/api/bookings/${id}/detail/`;

        const response = await fetch(endpoint);
        const data = await response.json();

        // Giả lập mapping dữ liệu từ API về chuẩn hiển thị
        // Trong thực tế, bạn map theo cấu trúc JSON của backend
        const mappedData: BookingData = {
          pnr: data.pnr || formatPNR(id),
          clinic_name: data.clinic?.name || "Minh Sinh Dental Central",
          clinic_address: data.clinic?.address || "123 Đường ABC, Quận 1, TP. HCM",
          appointment_date: data.appointment_date || "2024-12-25",
          passengers: Array.isArray(data.passengers) ? data.passengers : [data],
          total_amount: data.total_price || data.price || 0,
        };

        setBookingData(mappedData);
      } catch (error) {
        console.error("Error fetching booking:", error);
      } finally {
        setLoading(false);
      }
    };

    if (id) fetchBookingDetails();
  }, [id]);

  const handlePrint = () => {
    window.print();
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-cyan-600"></div>
      </div>
    );
  }

  if (!bookingData) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center">
        <h2 className="text-xl font-semibold">Không tìm thấy thông tin đặt lịch</h2>
        <button onClick={() => router.push("/")} className="mt-4 text-cyan-600 flex items-center">
          <Home className="mr-2 w-4 h-4" /> Quay lại trang chủ
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-100 py-12 px-4 sm:px-6 lg:px-8 print:bg-white print:p-0">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl mx-auto"
      >
        {/* Success Header */}
        <div className="text-center mb-8 print:hidden">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
            <CheckCircle2 className="w-10 h-10 text-green-600" />
          </div>
          <h1 className="text-3xl font-bold text-slate-900">Đặt lịch thành công!</h1>
          <p className="text-slate-600 mt-2">Cảm ơn bạn đã tin tưởng Minh Sinh Dental Airways.</p>
        </div>

        {/* Boarding Pass Ticket */}
        <div 
          ref={ticketRef}
          className="relative bg-white shadow-2xl rounded-3xl overflow-hidden border border-slate-200 print:shadow-none print:border-slate-300"
        >
          {/* Ticket Header (Aviation Style) */}
          <div className="bg-gradient-to-r from-slate-900 via-slate-800 to-cyan-900 text-white p-6 sm:p-8 relative">
            <div className="flex justify-between items-start">
              <div>
                <div className="flex items-center space-x-2 mb-1">
                  <PlaneTakeoff className="w-6 h-6 text-cyan-400" />
                  <span className="tracking-[0.2em] font-bold text-sm uppercase">Minh Sinh Dental Airways</span>
                </div>
                <h2 className="text-2xl font-black tracking-tighter italic">BOARDING PASS</h2>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-400 uppercase tracking-widest">Booking Reference</p>
                <p className="text-3xl font-mono font-bold text-cyan-400">{bookingData.pnr}</p>
              </div>
            </div>

            {/* Decorative Barcode Element */}
            <div className="mt-6 flex justify-between items-end">
              <div className="flex space-x-8">
                <div>
                  <p className="text-[10px] uppercase text-slate-400">Gate / Clinic</p>
                  <p className="font-bold text-lg">{bookingData.clinic_name}</p>
                </div>
                <div>
                  <p className="text-[10px] uppercase text-slate-400">Flight Date</p>
                  <p className="font-bold text-lg">{bookingData.appointment_date}</p>
                </div>
              </div>
              <div className="bg-white p-1 rounded-sm print:hidden">
                <QrCode className="w-12 h-12 text-slate-900" />
              </div>
            </div>
          </div>

          {/* Perforation Line */}
          <div className="relative h-6 bg-white flex items-center justify-center overflow-hidden">
            <div className="absolute left-[-12px] w-6 h-6 bg-slate-100 rounded-full border border-slate-200 shadow-inner"></div>
            <div className="w-full border-t-2 border-dashed border-slate-200 mx-4"></div>
            <div className="absolute right-[-12px] w-6 h-6 bg-slate-100 rounded-full border border-slate-200 shadow-inner"></div>
          </div>

          {/* Ticket Body */}
          <div className="p-6 sm:p-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="flex items-start space-x-3">
                <MapPin className="w-5 h-5 text-cyan-600 mt-1" />
                <div>
                  <p className="text-xs text-slate-500 uppercase font-bold">Địa điểm khám</p>
                  <p className="text-sm font-medium text-slate-800">{bookingData.clinic_address}</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Calendar className="w-5 h-5 text-cyan-600 mt-1" />
                <div>
                  <p className="text-xs text-slate-500 uppercase font-bold">Ngày hẹn</p>
                  <p className="text-sm font-medium text-slate-800">{bookingData.appointment_date}</p>
                </div>
              </div>
              <div className="flex items-start space-x-3">
                <Clock className="w-5 h-5 text-cyan-600 mt-1" />
                <div>
                  <p className="text-xs text-slate-500 uppercase font-bold">Boarding Time</p>
                  <p className="text-sm font-medium text-slate-800">Vui lòng đến trước 15 phút</p>
                </div>
              </div>
            </div>

            {/* Passenger List */}
            <div className="space-y-4">
              <h3 className="text-xs font-black text-slate-400 uppercase tracking-[0.2em] border-b pb-2">Passenger Manifest</h3>
              {bookingData.passengers.map((passenger, index) => (
                <div key={index} className="flex flex-wrap items-center justify-between p-4 bg-slate-50 rounded-xl border border-slate-100 group hover:border-cyan-200 transition-colors">
                  <div className="flex items-center space-x-4 min-w-[200px]">
                    <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center border border-slate-200 text-slate-400 group-hover:text-cyan-600">
                      <User className="w-5 h-5" />
                    </div>
                    <div>
                      <p className="text-[10px] text-slate-500 uppercase font-bold">Passenger</p>
                      <p className="font-bold text-slate-900 uppercase">{passenger.full_name}</p>
                    </div>
                  </div>
                  
                  <div className="mt-2 sm:mt-0">
                    <p className="text-[10px] text-slate-500 uppercase font-bold">Service Class</p>
                    <div className="flex items-center text-cyan-700">
                      <Stethoscope className="w-3 h-3 mr-1" />
                      <span className="text-sm font-semibold">{passenger.service_name}</span>
                    </div>
                  </div>

                  <div className="mt-2 sm:mt-0 text-right">
                    <p className="text-[10px] text-slate-500 uppercase font-bold">Price</p>
                    <p className="text-sm font-mono font-bold text-slate-900">{formatCurrency(passenger.price)}</p>
                  </div>

                  <div className="mt-2 sm:mt-0">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-800 border border-green-200">
                      CONFIRMED
                    </span>
                  </div>
                </div>
              ))}
            </div>

            {/* Total Section */}
            <div className="mt-8 pt-6 border-t border-slate-100 flex justify-between items-center">
              <div>
                <p className="text-sm text-slate-500 italic">Hệ thống đã gửi email xác nhận kèm mã QR vào hòm thư của bạn.</p>
              </div>
              <div className="text-right">
                <p className="text-xs text-slate-500 uppercase font-bold">Group Total</p>
                <p className="text-2xl font-black text-slate-900">{formatCurrency(bookingData.total_amount)}</p>
              </div>
            </div>
          </div>

          {/* Footer Barcode */}
          <div className="bg-slate-50 p-4 flex flex-col items-center justify-center space-y-2 border-t border-slate-100">
             <div className="h-12 w-full max-w-xs bg-[url('https://www.cognex.com/api/Sitecore/Barcode/Get?type=Code128&value=MINHSINH-DENTAL')] bg-repeat-x opacity-70"></div>
             <p className="text-[10px] font-mono text-slate-400 tracking-[0.5em]">{bookingData.pnr}-{id}</p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-10 flex flex-wrap justify-center gap-4 print:hidden">
          <button 
            onClick={handlePrint}
            className="flex items-center px-6 py-3 bg-slate-900 text-white rounded-full font-bold hover:bg-slate-800 transition-all shadow-lg hover:shadow-xl active:scale-95"
          >
            <Printer className="w-5 h-5 mr-2" />
            In thẻ Boarding Pass
          </button>
          
          <button 
            className="flex items-center px-6 py-3 bg-white text-slate-900 border border-slate-200 rounded-full font-bold hover:bg-slate-50 transition-all shadow-sm active:scale-95"
          >
            <Download className="w-5 h-5 mr-2" />
            Tải biên nhận (PDF)
          </button>

          <button 
            onClick={() => router.push("/")}
            className="flex items-center px-6 py-3 bg-cyan-600 text-white rounded-full font-bold hover:bg-cyan-700 transition-all shadow-lg hover:shadow-xl active:scale-95"
          >
            <Home className="w-5 h-5 mr-2" />
            Về Trang Chủ
          </button>
        </div>

        <p className="text-center mt-8 text-slate-400 text-xs print:hidden">
          © 2024 Minh Sinh Dental Airways. All rights reserved. <br/>
          Hệ thống đặt lịch hàng không nha khoa tiêu chuẩn quốc tế.
        </p>
      </motion.div>

      {/* Print Styles */}
      <style jsx global>{`
        @media print {
          body {
            background: white !important;
          }
          .print\:hidden {
            display: none !important;
          }
          .print\:shadow-none {
            box-shadow: none !important;
          }
          .print\:border-slate-300 {
            border: 1px solid #cbd5e1 !important;
          }
        }
      `}</style>
    </div>
  );
}
