import Link from 'next/link';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-blue-50">
      <h1 className="text-5xl font-bold text-blue-900 mb-6">Chào mừng đến với Nha khoa Minh Sinh</h1>
      <p className="text-xl text-gray-600 mb-10 text-center max-w-2xl">
        Hệ thống phòng khám nha khoa tiêu chuẩn quốc tế. Đội ngũ bác sĩ chuyên môn cao, trang thiết bị hiện đại.
      </p>
      <Link href="/booking" className="px-8 py-4 bg-blue-600 text-white font-bold rounded-full hover:bg-blue-700 transition shadow-lg">
        Đặt lịch ngay
      </Link>
    </main>
  );
}