import Link from 'next/link';

export default async function BookingSuccessPage({ params }: { params: Promise<{ id: string | string[] }> }) {
    const resolvedParams = await params;

    // Tách chuỗi ID nếu khách đặt nhiều người
    const rawId = Array.isArray(resolvedParams.id) ? resolvedParams.id.join('-') : (resolvedParams.id || '');
    const ids = rawId.split(/[,-]/).filter(Boolean);

    // Gọi API lấy dữ liệu song song cho tất cả các Booking
    const bookingsData = await Promise.all(
        ids.map(async (id) => {
            try {
                const res = await fetch(`http://backend:8000/api/bookings/${id}/`, { cache: 'no-store' });
                if (res.ok) return await res.json();
            } catch (e) {}
            return null;
        })
    );
    const bookings = bookingsData.filter(b => b && !b.error && b.id);

    return (
        <div className="container mx-auto py-12 px-4 max-w-4xl">
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
                <div className="bg-green-500 text-white text-center py-10 px-4">
                    <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                        <svg className="w-10 h-10 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7"></path></svg>
                    </div>
                    <h1 className="text-3xl md:text-4xl font-bold mb-2">Đặt Lịch Thành Công!</h1>
                    <p className="text-green-100 text-lg">Cảm ơn bạn đã tin tưởng Nha Khoa Minh Sinh</p>
                </div>
                
                <div className="p-6 md:p-10">
                    <h2 className="text-xl font-bold text-gray-800 mb-6 border-b pb-3">Chi tiết các lịch hẹn ({bookings.length}):</h2>
                    <div className="space-y-6">
                        {bookings.length > 0 ? bookings.map((booking, idx) => (
                            <div key={idx} className="bg-blue-50 p-6 rounded-xl border border-blue-100 shadow-sm relative overflow-hidden">
                                <div className="absolute top-0 right-0 bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-bl-lg">#{booking.id}</div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Khách hàng</p>
                                        <p className="font-bold text-gray-800 text-lg">{booking.customer_name || booking.name || 'Khách hàng'}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Số điện thoại</p>
                                        <p className="font-semibold text-gray-800">{booking.customer_phone || booking.phone || '---'}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Dịch vụ</p>
                                        <p className="font-semibold text-blue-700">{booking.service_name || booking.category_name || 'Khám tổng quát'}</p>
                                    </div>
                                    <div>
                                        <p className="text-sm text-gray-500 mb-1">Thời gian (Dự kiến)</p>
                                        <p className="font-semibold text-gray-800">{booking.time || booking.start_time} - {booking.date || booking.booking_date || booking.start_date}</p>
                                    </div>
                                </div>
                            </div>
                        )) : (
                            <p className="text-center text-gray-500">Đang tải chi tiết hoặc mã lịch không hợp lệ...</p>
                        )}
                    </div>
                    
                    <div className="mt-10 text-center">
                        <Link href="/" className="inline-block bg-blue-600 text-white font-bold py-3 px-10 rounded-full shadow-md hover:bg-blue-700 hover:shadow-lg transition-all duration-300">
                            Về trang chủ
                        </Link>
                    </div>
                </div>
            </div>
        </div>
    );
}
