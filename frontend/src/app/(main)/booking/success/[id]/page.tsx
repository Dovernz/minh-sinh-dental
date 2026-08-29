import Link from "next/link";

export default async function BookingSuccessPage({ params }: { params: Promise<{ id: string }> }) {
    // Giải quyết lỗi Promise của Next.js 15+
    const resolvedParams = await params;
    const id = resolvedParams.id;

    // Gọi API lấy dữ liệu thực (Server Component)
    let booking = null;
    try {
        const res = await fetch(`http://backend:8000/api/bookings/${id}/detail/`, { cache: 'no-store' });
        if (res.ok) {
            booking = await res.json();
        }
    } catch (error) {
        console.error("Lỗi fetch dữ liệu booking:", error);
    }

    const clinicName = booking?.clinic_name || "Nha Khoa Minh Sinh";
    const clinicAddress = booking?.clinic_address || "Hồ Chí Minh";

    return (
        <div className="max-w-3xl mx-auto p-8 mt-10 bg-white rounded-xl shadow-lg border border-gray-100">
            <div className="text-center mb-8">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-green-100 rounded-full mb-4">
                    <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
                    </svg>
                </div>
                <h1 className="text-3xl font-bold text-gray-800">Đặt Lịch Thành Công!</h1>
                <p className="text-gray-500 mt-2">Mã lịch hẹn của bạn là: <strong className="text-blue-600">#{id}</strong></p>
            </div>

            {booking && (
                <div className="mb-8 p-6 bg-blue-50 rounded-lg border border-blue-100 text-gray-700">
                    <h3 className="font-bold text-lg mb-4 text-blue-800">Thông tin đặt lịch:</h3>
                    <ul className="space-y-2">
                        <li><strong>Khách hàng:</strong> {booking.customer_name}</li>
                        <li><strong>Dịch vụ:</strong> {booking.category_name}</li>
                        <li><strong>Thời gian:</strong> {booking.start_time}</li>
                    </ul>
                </div>
            )}

            <div className="mb-8">
                <h2 className="text-lg font-bold text-gray-800 mb-2">Đến khám tại: {clinicName}</h2>
                <p className="text-gray-600 mb-4">📍 {clinicAddress}</p>
                <div className="w-full h-80 rounded-lg overflow-hidden border border-gray-200 shadow-sm">
                    <iframe 
                        width="100%" height="100%" frameBorder="0" style={{ border: 0 }}
                        referrerPolicy="no-referrer-when-downgrade" 
                        src={`https://www.google.com/maps?q=${encodeURIComponent(clinicName)},+${encodeURIComponent(clinicAddress)}&output=embed`} 
                        allowFullScreen>
                    </iframe>
                </div>
            </div>

            <div className="text-center">
                <Link href="/" className="inline-block px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow hover:bg-blue-700 transition-colors">
                    Về trang chủ
                </Link>
            </div>
        </div>
    );
}