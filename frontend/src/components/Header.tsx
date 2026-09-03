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
            <Link href="#" className="text-gray-600 hover:text-blue-600 font-medium flex items-center gap-1 transition-colors py-4">
              Thông tin phòng khám
              <svg className="w-4 h-4 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
              </svg>
            </Link>
            
            {/* Dropdown Dịch vụ */}
            <div className="relative group">
                <button className="text-gray-600 hover:text-blue-600 font-medium flex items-center gap-1 transition-colors py-4">
                    Dịch vụ
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                </button>
                {/* Khung Dropdown */}
                <div className="absolute top-full left-0 w-60 bg-white rounded-xl shadow-xl border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform translate-y-2 group-hover:translate-y-0 z-50 overflow-hidden">
                    <Link href="/dich-vu/nieng-rang" className="block px-5 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 border-b border-gray-50 transition-colors">Niềng răng - Chỉnh nha</Link>
                    <Link href="/dich-vu/nho-rang" className="block px-5 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors">Nhổ răng khôn</Link>
                </div>
            </div>

            {/* Dropdown Tin tức & Blog */}
            <div className="relative group flex items-center">
                <Link href="/blog" className="text-gray-600 hover:text-blue-600 font-medium flex items-center gap-1 transition-colors py-4">
                    Tin tức & Blog
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                </Link>
                <div className="absolute top-[100%] left-0 w-56 bg-white rounded-xl shadow-xl border border-gray-100 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-300 transform translate-y-2 group-hover:translate-y-0 z-50 overflow-hidden">
                    <Link href="/blog?category=kien-thuc" className="block px-5 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 border-b border-gray-50 transition-colors">Kiến thức y khoa</Link>
                    <Link href="/blog?category=khuyen-mai" className="block px-5 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors">Khuyến mại</Link>
                </div>
            </div>
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
