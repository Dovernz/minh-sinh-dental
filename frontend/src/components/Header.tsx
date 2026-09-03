'use client';
import { useState } from 'react';
import Link from 'next/link';

export default function Header() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isServiceOpen, setIsServiceOpen] = useState(false);
  const [isBlogOpen, setIsBlogOpen] = useState(false);

  return (
    <header className="w-full bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          
          {/* Nút Hamburger (Mobile) */}
          <div className="flex items-center md:hidden">
              <button onClick={() => setIsMobileMenuOpen(true)} className="text-gray-600 hover:text-blue-600 p-2">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      {isMobileMenuOpen ? (
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                      ) : (
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                      )}
                  </svg>
              </button>
          </div>

          {/* Logo (Căn giữa trên Mobile, Trái trên Desktop) */}
          <div className="flex-1 flex justify-center md:justify-start">
            <Link href="/" className="flex items-center gap-2">
              <img src="/logo.png" alt="Logo" className="w-14 h-14 object-contain rounded-full border shadow-sm bg-white" />
              <span className="font-bold text-xl md:text-2xl text-blue-900 tracking-tight">Nha Khoa Minh Sinh</span>
            </Link>
          </div>

          {/* Navigation (Desktop) */}
          <nav className="hidden md:flex space-x-8 items-center">
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
            
            <Link href="/booking" className="ml-8 px-6 py-2.5 bg-[rgb(37,99,235)] hover:bg-[rgb(29,78,216)] text-white font-semibold rounded-full transition-all duration-300 transform hover:-translate-y-1 shadow-lg hover:shadow-[0_8px_20px_rgb(37,99,235,0.4)]">
              Đặt lịch ngay
            </Link>
          </nav>
          
          {/* Một div rỗng bên phải để cân bằng với nút hamburger bên trái trên mobile */}
          <div className="md:hidden w-10"></div>
        </div>
      </div>
      
      {/* --- KHỐI MOBILE MENU TRƯỢT (OFF-CANVAS 3/4 MÀN HÌNH) --- */}
            
      {/* 1. Lớp màng đen lót nền (Bấm vào phần mờ để đóng) */}
      <div 
          className={`fixed inset-0 bg-black/50 z-[55] transition-opacity duration-300 md:hidden ${isMobileMenuOpen ? 'opacity-100 visible' : 'opacity-0 invisible'}`}
          onClick={() => setIsMobileMenuOpen(false)}
      ></div>

      {/* 2. Khung Menu trượt bên trái */}
      <div className={`fixed inset-y-0 left-0 w-[75vw] max-w-sm bg-white z-[60] shadow-2xl transform transition-transform duration-300 ease-in-out md:hidden flex flex-col ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
          
          {/* Thanh tiêu đề & Nút tắt (X) */}
          <div className="flex justify-between items-center h-20 px-4 border-b border-gray-100">
              <span className="font-bold text-lg text-blue-800 line-clamp-1">Nha Khoa Minh Sinh</span>
              <button onClick={() => setIsMobileMenuOpen(false)} className="text-gray-500 hover:text-red-500 p-2 ml-auto">
                  <svg className="w-7 h-7" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" /></svg>
              </button>
          </div>

          {/* Danh sách Menu & Menu con */}
          <div className="flex-1 overflow-y-auto py-4 px-4 space-y-2">
              <Link href="/" onClick={() => setIsMobileMenuOpen(false)} className="block px-4 py-3 text-base font-medium text-gray-800 hover:bg-blue-50 rounded-xl">
                  Thông tin phòng khám
              </Link>

              {/* Khối Dịch vụ */}
              <div>
                  <button onClick={() => setIsServiceOpen(!isServiceOpen)} className="w-full flex justify-between items-center px-4 py-3 text-base font-medium text-gray-800 hover:bg-blue-50 rounded-xl">
                      Dịch vụ
                      <svg className={`w-5 h-5 transform transition-transform ${isServiceOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                  </button>
                  {isServiceOpen && (
                      <div className="pl-6 pr-4 py-2 space-y-2 bg-gray-50 rounded-lg mt-1">
                          <Link href="/dich-vu/nieng-rang" onClick={() => setIsMobileMenuOpen(false)} className="block py-2 text-gray-600 text-sm">Niềng răng - Chỉnh nha</Link>
                          <Link href="/dich-vu/nho-rang" onClick={() => setIsMobileMenuOpen(false)} className="block py-2 text-gray-600 text-sm">Nhổ răng khôn</Link>
                      </div>
                  )}
              </div>

              {/* Khối Tin tức & Blog */}
              <div>
                  <button onClick={() => setIsBlogOpen(!isBlogOpen)} className="w-full flex justify-between items-center px-4 py-3 text-base font-medium text-gray-800 hover:bg-blue-50 rounded-xl">
                      Tin tức & Blog
                      <svg className={`w-5 h-5 transform transition-transform ${isBlogOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" /></svg>
                  </button>
                  {isBlogOpen && (
                      <div className="pl-6 pr-4 py-2 space-y-2 bg-gray-50 rounded-lg mt-1">
                          <Link href="/blog?category=kien-thuc" onClick={() => setIsMobileMenuOpen(false)} className="block py-2 text-gray-600 text-sm">Kiến thức y khoa</Link>
                          <Link href="/blog?category=khuyen-mai" onClick={() => setIsMobileMenuOpen(false)} className="block py-2 text-gray-600 text-sm">Khuyến mại</Link>
                      </div>
                  )}
              </div>
          </div>

          {/* Khu vực Nút Đặt lịch cố định ở đáy */}
          <div className="p-4 border-t border-gray-100 pb-8">
              <Link href="/dat-lich" onClick={() => setIsMobileMenuOpen(false)} className="flex justify-center items-center w-full bg-blue-600 text-white px-4 py-3 rounded-full font-bold text-base hover:bg-blue-700 shadow-lg transition-colors">
                  Đặt lịch ngay
              </Link>
          </div>
      </div>
      </header>
  );
}
