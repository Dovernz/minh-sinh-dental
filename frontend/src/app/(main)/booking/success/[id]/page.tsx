"use client";
import React, { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

export default function BookingSuccessPage() {
    const params = useParams();
    const id = params?.id;
    const [bookings, setBookings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        const loader = document.getElementById('safe-loader');
        if (loader) loader.remove(); // Hủy màn chắn loading của trang trước

        if (!id || id === 'undefined') return;
        
        const idStr = Array.isArray(id) ? id.join(',') : String(id);
        const ids = decodeURIComponent(idStr).split(',').filter(v => v && v !== 'undefined');
        
        if (ids.length === 0) {
            setLoading(false);
            return;
        }

        Promise.all(ids.map(bookId => 
            fetch(`http://localhost:8000/api/bookings/${bookId}/detail/`).then(res => res.ok ? res.json() : null)
        )).then(data => {
            let flatData = [];
            data.forEach(item => {
                if (item) {
                    if (Array.isArray(item)) flatData.push(...item);
                    else flatData.push(item);
                }
            });
            setBookings(flatData);
            setLoading(false);
        }).catch(err => {
            console.error("Lỗi:", err);
            setError(String(err));
            setLoading(false);
        });
    }, [id]);

    return (
        <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-3xl mx-auto">
                <div className="bg-white rounded-2xl shadow-xl overflow-hidden border border-gray-100">
                    <div className="bg-green-500 py-8 px-6 text-center">
                        <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-white mb-4 shadow-sm">
                            <svg className="h-8 w-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                        </div>
                        <h2 className="text-3xl font-extrabold text-white tracking-tight">Đặt Lịch Thành Công!</h2>
                        <p className="mt-2 text-green-100 text-lg">Cảm ơn bạn đã tin tưởng Nha Khoa Minh Sinh</p>
                    </div>
                    
                    <div className="p-8">
                        <h3 className="text-xl font-bold text-gray-900 mb-6 border-b pb-3">Chi tiết lịch hẹn ({bookings.length}):</h3>
                        
                        
                        {error && (
                            <div className="bg-red-50 text-red-600 p-4 rounded-lg mb-6 border border-red-200">
                                <b>Lỗi kết nối API:</b> {error}
                                <br/> Máy chủ không tìm thấy thông tin hoặc đang quá tải.
                            </div>
                        )}
                        {loading ? (
                            <div className="flex flex-col items-center py-8 space-y-4">
                                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
                                <p className="text-gray-500">Đang tải chi tiết lịch hẹn...</p>
                            </div>
                        ) : bookings.length > 0 ? (
                            <div className="space-y-6">
                                {bookings.map((bk, idx) => (
                                    <div key={idx} className="bg-blue-50 border border-blue-100 rounded-xl p-6 relative hover:shadow-md transition-shadow">
                                        <div className="absolute top-0 right-0 bg-blue-500 text-white px-4 py-1.5 rounded-bl-lg rounded-tr-xl text-sm font-bold shadow-sm">Mã: #{bk.id}</div>
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
                                            <div>
                                                <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider">Khách hàng</p>
                                                <p className="font-bold text-gray-900 text-lg mt-1">{bk.customer_name}</p>
                                            </div>
                                            <div>
                                                <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider">Dịch vụ</p>
                                                <p className="font-bold text-blue-600 text-lg mt-1">{bk.category_name}</p>
                                            </div>
                                            <div>
                                                <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider">Thời gian</p>
                                                <p className="font-bold text-gray-900 text-lg mt-1">{bk.start_time}</p>
                                            </div>
                                            <div>
                                                <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider">Cơ sở</p>
                                                <p className="font-bold text-gray-900 text-lg mt-1">{bk.clinic_name}</p>
                                                <p className="text-sm text-gray-500 mt-1">{bk.clinic_address}</p>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="text-center py-10 bg-gray-50 rounded-xl border border-dashed border-gray-300">
                                <p className="text-gray-600 font-medium">Mã lịch không hợp lệ hoặc không tìm thấy dữ liệu.</p>
                            </div>
                        )}

                        <div className="mt-10 flex justify-center">
                            <Link href="/" className="px-10 py-3.5 bg-blue-600 text-white font-bold rounded-xl hover:bg-blue-700 transition-all shadow-lg hover:shadow-blue-500/30">
                                Về Trang Chủ
                            </Link>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
