'use client';
import { useState } from 'react';
import Link from 'next/link';

export default function Header({ menus = [] }: { menus?: any[] }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  
  // State for mobile submenus
  const [openSubMenus, setOpenSubMenus] = useState<{[key: string]: boolean}>({});

  const toggleSubMenu = (id: string) => {
    setOpenSubMenus(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <header className="w-full bg-white shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-20">
          
          {/* Nút Hamburger (Mobile) */}
          <div className="flex items-center lg:hidden">
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

          {/* Logo */}
          <div className="flex-1 flex justify-center lg:justify-start">
            <Link href="/" className="flex items-center gap-2">
              <img src="/logo.png" alt="Logo" className="w-14 h-14 object-contain rounded-full border shadow-sm bg-white" />
              <span className="font-bold text-xl lg:text-2xl text-blue-900 tracking-tight whitespace-nowrap">Nha Khoa Minh Sinh</span>
            </Link>
          </div>

          {/* Navigation (Desktop) */}
          <ul className="hidden lg:flex items-center gap-8">
            {menus.map((menu: any) => (
                <li key={menu.id} className="relative group">
                    {menu.children && menu.children.length > 0 ? (
                        <>
                            <Link href={menu.url || "#"} className="flex items-center gap-1 font-medium text-gray-600 hover:text-blue-600 transition-colors py-4">
                                {menu.title} 
                                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7"></path></svg>
                            </Link>

                            <ul className="absolute hidden group-hover:block top-full left-0 mt-0 w-56 bg-white shadow-lg rounded-xl border border-gray-100 overflow-hidden z-50">
                                {menu.children.map((child: any) => (
                                    <li key={child.id} className="border-b border-gray-50 last:border-0">
                                        <Link href={child.url || "#"} className="block px-4 py-3 text-gray-600 hover:bg-blue-50 hover:text-blue-600 transition-colors">
                                            {child.title}
                                        </Link>
                                    </li>
                                ))}
                            </ul>
                        </>
                    ) : (
                        <Link href={menu.url || "#"} className="flex items-center gap-1 font-medium text-gray-600 hover:text-blue-600 transition-colors py-4">
                            {menu.title}
                        </Link>
                    )}
                </li>
            ))}
          </ul>

          {/* Nút Đặt lịch (Desktop) */}
          <div className="hidden lg:flex items-center ml-8">
            <Link href="/booking" className="bg-blue-600 hover:bg-blue-700 text-white font-medium px-6 py-2.5 rounded-full transition-colors shadow-md hover:shadow-lg flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
              Đặt lịch ngay
            </Link>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      <div className={`fixed inset-0 bg-gray-900/50 z-40 lg:hidden transition-opacity duration-300 ${isMobileMenuOpen ? 'opacity-100' : 'opacity-0 pointer-events-none'}`} onClick={() => setIsMobileMenuOpen(false)} />
      
      <div className={`fixed inset-y-0 left-0 w-[280px] bg-white z-50 transform transition-transform duration-300 ease-in-out flex flex-col shadow-2xl lg:hidden ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}`}>
        <div className="flex items-center justify-between p-4 border-b">
            <div className="flex items-center gap-2">
                <img src="/logo.png" alt="Logo" className="w-10 h-10 object-contain rounded-full border" />
                <span className="font-bold text-lg text-blue-900">Minh Sinh</span>
            </div>
            <button onClick={() => setIsMobileMenuOpen(false)} className="p-2 text-gray-500 hover:bg-gray-100 rounded-full">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>

        <div className="flex-1 overflow-y-auto py-4">
            <nav className="px-4 space-y-1">
                {menus.map((menu: any) => (
                  <div key={menu.id}>
                    {menu.children && menu.children.length > 0 ? (
                      <>
                        <button onClick={() => toggleSubMenu(menu.id)} className="w-full flex items-center justify-between px-3 py-3 text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg">
                          {menu.title}
                          <svg className={`w-5 h-5 transition-transform ${openSubMenus[menu.id] ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                          </svg>
                        </button>
                        {openSubMenus[menu.id] && (
                          <div className="pl-4 pr-2 py-2 space-y-1 bg-gray-50/50 rounded-lg mt-1">
                            {menu.children.map((child: any) => (
                              <Link key={child.id} href={child.url || "#"} onClick={() => setIsMobileMenuOpen(false)} className="block px-3 py-2 text-sm font-medium text-gray-600 hover:text-blue-600 hover:bg-white rounded-md">
                                {child.title}
                              </Link>
                            ))}
                          </div>
                        )}
                      </>
                    ) : (
                      <Link href={menu.url || "#"} onClick={() => setIsMobileMenuOpen(false)} className="flex items-center px-3 py-3 text-base font-medium text-gray-700 hover:text-blue-600 hover:bg-blue-50 rounded-lg">
                        {menu.title}
                      </Link>
                    )}
                  </div>
                ))}
            </nav>
        </div>

        <div className="p-4 border-t bg-gray-50">
            <Link href="/booking" onClick={() => setIsMobileMenuOpen(false)} className="w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-medium px-4 py-3 rounded-xl transition-colors shadow-sm">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
                Đặt lịch ngay
            </Link>
        </div>
      </div>
    </header>
  );
}
