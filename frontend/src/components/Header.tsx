import Link from 'next/link';

export default function Header() {
  return (
    <header className="w-full bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          
          {/* Logo & Tên */}
          <div className="flex-shrink-0 flex items-center gap-3">
            <Link href="/" className="flex items-center gap-2">
              <img src="/logo.png" alt="Logo" className="w-14 h-14 object-contain rounded-full border shadow-sm bg-white" />
              <span className="font-bold text-2xl text-blue-900 tracking-tight">Nha Khoa Minh Sinh</span>
            </Link>
          </div>

          {/* Navigation (Desktop) */}
          <nav className="hidden md:flex space-x-10 items-center">
            <Link href="#" className="text-gray-600 hover:text-blue-600 font-medium flex items-center gap-1 transition-colors">
              Thông tin phòng khám
              <svg className="w-4 h-4 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
              </svg>
            </Link>
            <Link href="#" className="text-gray-600 hover:text-blue-600 font-medium flex items-center gap-1 transition-colors">
              Dịch vụ
              <svg className="w-4 h-4 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
              </svg>
            </Link>
            <Link href="/blog" className="text-gray-600 hover:text-blue-600 font-medium flex items-center gap-1 transition-colors">
              Tin tức & Blog
            </Link>
          </nav>

          {/* CTA Button */}
          <div className="flex items-center">
            <Link
              href="/booking"
              className="px-6 py-2.5 bg-[rgb(37,99,235)] hover:bg-[rgb(29,78,216)] text-white font-semibold rounded-full transition-all duration-300 transform hover:-translate-y-1 shadow-lg hover:shadow-[0_8px_20px_rgb(37,99,235,0.4)]"
            >
              Đặt lịch ngay
            </Link>
          </div>

        </div>
      </div>
    </header>
  );
}
