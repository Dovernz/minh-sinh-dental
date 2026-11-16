"use client";

import React, { useState, useEffect, useMemo } from 'react';
import { 
  Search, 
  Users, 
  User, 
  CreditCard, 
  Banknote, 
  QrCode, 
  Printer, 
  RefreshCw, 
  Clock, 
  History, 
  CheckCircle2, 
  AlertCircle,
  X,
  ChevronRight,
  Receipt
} from 'lucide-react';

// --- Types ---
type PaymentStatus = 'Chờ thanh toán' | 'Đã thanh toán';
type PaymentMethod = 'Tiền mặt' | 'Chuyển khoản' | 'Quẹt thẻ';

interface Service {
  id: string;
  name: string;
  price: number;
}

interface Customer {
  id: string;
  name: string;
  phone: string;
  pnr?: string;
  services: Service[];
  status: PaymentStatus;
  checkInTime: string;
}

interface GroupPNR {
  pnr: string;
  representative: string;
  customers: Customer[];
  date: string;
  branch: string;
}

interface Transaction {
  id: string;
  time: string;
  customerName: string;
  pnr?: string;
  amount: number;
  method: PaymentMethod;
  type: 'Gộp' | 'Lẻ';
}

// --- Mock Data ---
const MOCK_PNRS: GroupPNR[] = [
  {
    pnr: 'MS8888',
    representative: 'Nguyễn Văn A',
    date: '2023-10-27',
    branch: 'Cơ sở Quận 1',
    customers: [
      { id: 'C1', name: 'Nguyễn Văn A', phone: '0901234567', services: [{ id: 'S1', name: 'Nhổ răng khôn', price: 1500000 }], status: 'Chờ thanh toán', checkInTime: '08:30' },
      { id: 'C2', name: 'Trần Thị B', phone: '0907654321', services: [{ id: 'S2', name: 'Tẩy trắng răng', price: 2500000 }], status: 'Chờ thanh toán', checkInTime: '08:45' },
      { id: 'C3', name: 'Lê Văn C', phone: '0911223344', services: [{ id: 'S3', name: 'Cạo vôi răng', price: 500000 }], status: 'Chờ thanh toán', checkInTime: '09:00' },
    ]
  },
  {
    pnr: 'DENT01',
    representative: 'Phạm Minh Tuấn',
    date: '2023-10-27',
    branch: 'Cơ sở Quận 3',
    customers: [
      { id: 'C4', name: 'Phạm Minh Tuấn', phone: '0988888888', services: [{ id: 'S4', name: 'Trám răng', price: 400000 }], status: 'Chờ thanh toán', checkInTime: '10:15' },
      { id: 'C5', name: 'Hoàng Mỹ Linh', phone: '0977777777', services: [{ id: 'S5', name: 'Niềng răng trả góp', price: 5000000 }], status: 'Chờ thanh toán', checkInTime: '10:20' },
    ]
  }
];

export default function POSPage() {
  // --- States ---
  const [activeTab, setActiveTab] = useState<'pnr' | 'individual' | 'history'>('pnr');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [pnrSearch, setPnrSearch] = useState('');
  const [selectedGroup, setSelectedGroup] = useState<GroupPNR | null>(null);
  const [individualSearch, setIndividualSearch] = useState('');
  const [selectedCustomer, setSelectedCustomer] = useState<Customer | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<PaymentMethod>('Tiền mặt');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [showInvoice, setShowInvoice] = useState(false);
  const [lastInvoice, setLastInvoice] = useState<any>(null);

  // --- Clock Effect ---
  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // --- Calculations ---
  const groupSubtotal = useMemo(() => {
    if (!selectedGroup) return 0;
    return selectedGroup.customers.reduce((sum, c) => sum + c.services.reduce((s, ser) => s + ser.price, 0), 0);
  }, [selectedGroup]);

  const groupDiscount = useMemo(() => {
    if (!selectedGroup || selectedGroup.customers.length < 3) return 0;
    return groupSubtotal * 0.1; // 10% discount for 3+ people
  }, [selectedGroup, groupSubtotal]);

  const groupTotal = groupSubtotal - groupDiscount;

  const individualTotal = useMemo(() => {
    if (!selectedCustomer) return 0;
    return selectedCustomer.services.reduce((sum, s) => sum + s.price, 0);
  }, [selectedCustomer]);

  const todayRevenue = useMemo(() => {
    return transactions.reduce((sum, t) => sum + t.amount, 0);
  }, [transactions]);

  // --- Handlers ---
  const handlePnrSearch = (code?: string) => {
    const searchCode = (code || pnrSearch).toUpperCase();
    const found = MOCK_PNRS.find(g => g.pnr === searchCode);
    if (found) {
      setSelectedGroup(found);
      setPnrSearch(searchCode);
    } else {
      alert("Không tìm thấy mã PNR này!");
    }
  };

  const handleIndividualSearch = () => {
    // Search across all PNRs for a customer
    const allCustomers = MOCK_PNRS.flatMap(g => g.customers);
    const found = allCustomers.find(c => 
      c.name.toLowerCase().includes(individualSearch.toLowerCase()) || 
      c.phone.includes(individualSearch) ||
      c.id.toLowerCase() === individualSearch.toLowerCase()
    );
    if (found) {
      setSelectedCustomer(found);
    } else {
      alert("Không tìm thấy khách hàng!");
    }
  };

  const processPayment = (type: 'Gộp' | 'Lẻ') => {
    const amount = type === 'Gộp' ? groupTotal : individualTotal;
    const name = type === 'Gộp' ? selectedGroup?.representative : selectedCustomer?.name;
    const pnr = type === 'Gộp' ? selectedGroup?.pnr : selectedCustomer?.pnr;

    const newTx: Transaction = {
      id: `TX${Math.floor(Math.random() * 100000)}`,
      time: currentTime.toLocaleTimeString('vi-VN'),
      customerName: name || 'N/A',
      pnr: pnr,
      amount: amount,
      method: paymentMethod,
      type: type
    };

    setTransactions([newTx, ...transactions]);
    setLastInvoice({ ...newTx, details: type === 'Gộp' ? selectedGroup : selectedCustomer });
    setShowInvoice(true);

    // Reset state after payment
    if (type === 'Gộp') setSelectedGroup(null);
    else setSelectedCustomer(null);
  };

  const getVietQRUrl = (amount: number, info: string) => {
    // Mock Bank Info: Vietcombank - 1234567890
    return `https://img.vietqr.io/image/vcb-1234567890-compact2.png?amount=${amount}&addInfo=${encodeURIComponent(info)}&accountName=NHA%20KHOA%20MINH%20SINH`;
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans">
      {/* --- Header --- */}
      <header className="bg-indigo-900 text-white p-4 shadow-lg sticky top-0 z-30">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-3">
            <div className="bg-white p-2 rounded-lg">
              <Receipt className="text-indigo-900 w-6 h-6" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">Hệ thống Thu Ngân - Minh Sinh Dental POS</h1>
              <div className="flex items-center gap-4 text-xs text-indigo-200 mt-1">
                <span className="flex items-center gap-1"><Clock size={14} /> {currentTime.toLocaleTimeString('vi-VN')} | {currentTime.toLocaleDateString('vi-VN')}</span>
                <span className="bg-indigo-700 px-2 py-0.5 rounded">Ca trực: Sáng (08:00 - 12:00)</span>
              </div>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <div className="text-right">
              <p className="text-xs text-indigo-300 uppercase font-semibold">Doanh thu ca trực</p>
              <p className="text-2xl font-mono font-bold text-emerald-400">
                {todayRevenue.toLocaleString('vi-VN')} <span className="text-sm">đ</span>
              </p>
            </div>
            <button 
              onClick={() => window.location.reload()}
              className="p-2 bg-indigo-800 hover:bg-indigo-700 rounded-full transition-colors"
            >
              <RefreshCw size={20} />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4 md:p-6">
        {/* --- Navigation Tabs --- */}
        <div className="flex bg-white p-1 rounded-xl shadow-sm mb-6 w-fit border border-slate-200">
          <button 
            onClick={() => setActiveTab('pnr')}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all ${activeTab === 'pnr' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-500 hover:bg-slate-100'}`}
          >
            <Users size={18} /> Thanh toán theo PNR
          </button>
          <button 
            onClick={() => setActiveTab('individual')}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all ${activeTab === 'individual' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-500 hover:bg-slate-100'}`}
          >
            <User size={18} /> Thanh toán lẻ
          </button>
          <button 
            onClick={() => setActiveTab('history')}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-lg font-medium transition-all ${activeTab === 'history' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-500 hover:bg-slate-100'}`}
          >
            <History size={18} /> Lịch sử giao dịch
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* --- Left Column: Search & Info --- */}
          <div className="lg:col-span-2 space-y-6">
            
            {activeTab === 'pnr' && (
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-6 border-b border-slate-100">
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Tra cứu mã PNR (6 ký tự)</label>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                      <input 
                        type="text" 
                        maxLength={6}
                        value={pnrSearch}
                        onChange={(e) => setPnrSearch(e.target.value.toUpperCase())}
                        placeholder="Nhập mã PNR (VD: MS8888)..."
                        className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none font-mono text-lg"
                      />
                    </div>
                    <button 
                      onClick={() => handlePnrSearch()}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-bold transition-all"
                    >
                      Tra cứu
                    </button>
                  </div>
                  <div className="flex gap-2 mt-3">
                    <span className="text-xs text-slate-500 self-center">Gợi ý:</span>
                    {MOCK_PNRS.map(m => (
                      <button key={m.pnr} onClick={() => handlePnrSearch(m.pnr)} className="text-xs bg-slate-100 hover:bg-indigo-50 text-indigo-600 px-2 py-1 rounded border border-slate-200">{m.pnr}</button>
                    ))}
                  </div>
                </div>

                {selectedGroup ? (
                  <div className="p-6 animate-in fade-in slide-in-from-bottom-2">
                    <div className="flex justify-between items-start mb-6 bg-indigo-50 p-4 rounded-xl border border-indigo-100">
                      <div>
                        <h3 className="text-indigo-900 font-bold text-lg flex items-center gap-2">
                          <Users size={20} /> Nhóm: {selectedGroup.representative}
                        </h3>
                        <p className="text-sm text-indigo-700">Mã PNR: <span className="font-mono font-bold">{selectedGroup.pnr}</span> • {selectedGroup.branch}</p>
                      </div>
                      <div className="text-right">
                        <span className="bg-amber-100 text-amber-700 text-xs font-bold px-3 py-1 rounded-full uppercase">Chờ thanh toán gộp</span>
                        <p className="text-xs text-slate-500 mt-1">Ngày khám: {selectedGroup.date}</p>
                      </div>
                    </div>

                    <div className="overflow-x-auto">
                      <table className="w-full text-left border-collapse">
                        <thead>
                          <tr className="text-slate-400 text-xs uppercase tracking-wider border-b border-slate-100">
                            <th className="pb-3 font-semibold">Khách hàng</th>
                            <th className="pb-3 font-semibold">Dịch vụ</th>
                            <th className="pb-3 font-semibold text-right">Đơn giá</th>
                            <th className="pb-3 font-semibold text-center">Trạng thái</th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-slate-50">
                          {selectedGroup.customers.map((c) => (
                            <tr key={c.id} className="group hover:bg-slate-50 transition-colors">
                              <td className="py-4">
                                <p className="font-bold text-slate-800">{c.name}</p>
                                <p className="text-xs text-slate-500">{c.phone}</p>
                              </td>
                              <td className="py-4">
                                {c.services.map(s => (
                                  <span key={s.id} className="text-sm text-slate-600 block">{s.name}</span>
                                ))}
                              </td>
                              <td className="py-4 text-right font-mono font-medium">
                                {c.services.reduce((sum, s) => sum + s.price, 0).toLocaleString('vi-VN')}đ
                              </td>
                              <td className="py-4 text-center">
                                <span className="inline-flex items-center gap-1 px-2 py-1 rounded-md bg-amber-50 text-amber-600 text-xs font-medium">
                                  <AlertCircle size={12} /> {c.status}
                                </span>
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </div>
                ) : (
                  <div className="p-20 text-center text-slate-400">
                    <Search size={48} className="mx-auto mb-4 opacity-20" />
                    <p>Vui lòng nhập mã PNR để hiển thị thông tin nhóm</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'individual' && (
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-6 border-b border-slate-100">
                  <label className="block text-sm font-semibold text-slate-700 mb-2">Tìm kiếm khách lẻ</label>
                  <div className="flex gap-2">
                    <div className="relative flex-1">
                      <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                      <input 
                        type="text" 
                        value={individualSearch}
                        onChange={(e) => setIndividualSearch(e.target.value)}
                        placeholder="Tên, SĐT hoặc Mã khách hàng..."
                        className="w-full pl-10 pr-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-indigo-500 outline-none"
                      />
                    </div>
                    <button 
                      onClick={handleIndividualSearch}
                      className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-xl font-bold transition-all"
                    >
                      Tìm kiếm
                    </button>
                  </div>
                </div>

                {selectedCustomer ? (
                  <div className="p-6 animate-in fade-in slide-in-from-bottom-2">
                    <div className="flex items-center gap-4 mb-8 bg-slate-50 p-6 rounded-2xl border border-slate-100">
                      <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600">
                        <User size={32} />
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-slate-800">{selectedCustomer.name}</h3>
                        <p className="text-slate-500">{selectedCustomer.phone} • ID: {selectedCustomer.id}</p>
                        {selectedCustomer.pnr && <span className="text-xs bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded mt-1 inline-block">Thuộc PNR: {selectedCustomer.pnr}</span>}
                      </div>
                    </div>

                    <h4 className="font-bold text-slate-700 mb-4 flex items-center gap-2">
                      <Receipt size={18} /> Chi tiết dịch vụ đã sử dụng
                    </h4>
                    <div className="space-y-3">
                      {selectedCustomer.services.map(s => (
                        <div key={s.id} className="flex justify-between items-center p-4 bg-white border border-slate-100 rounded-xl shadow-sm">
                          <span className="font-medium text-slate-700">{s.name}</span>
                          <span className="font-mono font-bold text-indigo-600">{s.price.toLocaleString('vi-VN')}đ</span>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="p-20 text-center text-slate-400">
                    <User size={48} className="mx-auto mb-4 opacity-20" />
                    <p>Tìm kiếm khách hàng để thực hiện thanh toán lẻ</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'history' && (
              <div className="bg-white rounded-2xl shadow-sm border border-slate-200 overflow-hidden">
                <div className="p-6 border-b border-slate-100 flex justify-between items-center">
                  <h3 className="font-bold text-slate-800 flex items-center gap-2"><History size={20} /> Giao dịch gần đây</h3>
                  <span className="text-xs text-slate-500">Hôm nay, {currentTime.toLocaleDateString('vi-VN')}</span>
                </div>
                <div className="overflow-x-auto">
                  <table className="w-full text-left">
                    <thead className="bg-slate-50 text-slate-500 text-xs uppercase">
                      <tr>
                        <th className="px-6 py-4 font-semibold">Thời gian</th>
                        <th className="px-6 py-4 font-semibold">Khách hàng / PNR</th>
                        <th className="px-6 py-4 font-semibold">Hình thức</th>
                        <th className="px-6 py-4 font-semibold text-right">Số tiền</th>
                        <th className="px-6 py-4 font-semibold text-center">Thao tác</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {transactions.length > 0 ? transactions.map((tx) => (
                        <tr key={tx.id} className="hover:bg-slate-50 transition-colors">
                          <td className="px-6 py-4 text-sm text-slate-500 font-mono">{tx.time}</td>
                          <td className="px-6 py-4">
                            <p className="font-bold text-slate-800 text-sm">{tx.customerName}</p>
                            <p className="text-xs text-indigo-600 font-mono">{tx.pnr || 'Khách lẻ'}</p>
                          </td>
                          <td className="px-6 py-4">
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                              tx.method === 'Tiền mặt' ? 'bg-emerald-50 text-emerald-600' : 
                              tx.method === 'Chuyển khoản' ? 'bg-blue-50 text-blue-600' : 'bg-purple-50 text-purple-600'
                            }`}>
                              {tx.method}
                            </span>
                          </td>
                          <td className="px-6 py-4 text-right font-mono font-bold text-slate-800">
                            {tx.amount.toLocaleString('vi-VN')}đ
                          </td>
                          <td className="px-6 py-4 text-center">
                            <button className="p-2 text-slate-400 hover:text-indigo-600 transition-colors">
                              <Printer size={18} />
                            </button>
                          </td>
                        </tr>
                      )) : (
                        <tr>
                          <td colSpan={5} className="px-6 py-20 text-center text-slate-400">Chưa có giao dịch nào trong ca làm việc</td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>

          {/* --- Right Column: Payment Panel --- */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-2xl shadow-xl border border-slate-200 p-6 sticky top-24">
              <h3 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
                <CreditCard size={20} className="text-indigo-600" /> Thanh toán
              </h3>

              {/* Summary */}
              <div className="space-y-3 mb-8">
                <div className="flex justify-between text-slate-500">
                  <span>Tạm tính:</span>
                  <span className="font-mono">{(activeTab === 'pnr' ? groupSubtotal : individualTotal).toLocaleString('vi-VN')}đ</span>
                </div>
                {activeTab === 'pnr' && groupDiscount > 0 && (
                  <div className="flex justify-between text-emerald-600 font-medium">
                    <span>Chiết khấu nhóm (10%):</span>
                    <span className="font-mono">-{groupDiscount.toLocaleString('vi-VN')}đ</span>
                  </div>
                )}
                <div className="pt-3 border-t border-dashed border-slate-200 flex justify-between items-end">
                  <span className="font-bold text-slate-800">Tổng cộng:</span>
                  <span className="text-3xl font-mono font-black text-indigo-700">
                    {(activeTab === 'pnr' ? groupTotal : individualTotal).toLocaleString('vi-VN')}đ
                  </span>
                </div>
              </div>

              {/* Payment Methods */}
              <div className="grid grid-cols-3 gap-2 mb-8">
                {(['Tiền mặt', 'Chuyển khoản', 'Quẹt thẻ'] as PaymentMethod[]).map((m) => (
                  <button
                    key={m}
                    onClick={() => setPaymentMethod(m)}
                    className={`flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all ${
                      paymentMethod === m 
                      ? 'border-indigo-600 bg-indigo-50 text-indigo-700' 
                      : 'border-slate-100 hover:border-slate-200 text-slate-500'
                    }`}
                  >
                    {m === 'Tiền mặt' && <Banknote size={20} />}
                    {m === 'Chuyển khoản' && <QrCode size={20} />}
                    {m === 'Quẹt thẻ' && <CreditCard size={20} />}
                    <span className="text-[10px] font-bold uppercase tracking-tighter">{m}</span>
                  </button>
                ))}
              </div>

              {/* QR Code Display */}
              {paymentMethod === 'Chuyển khoản' && (activeTab === 'pnr' ? selectedGroup : selectedCustomer) && (
                <div className="mb-8 p-4 bg-slate-50 rounded-2xl border border-slate-200 text-center animate-in zoom-in-95">
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Quét mã VietQR để thanh toán</p>
                  <img 
                    src={getVietQRUrl(
                      activeTab === 'pnr' ? groupTotal : individualTotal, 
                      activeTab === 'pnr' ? `THANH TOAN PNR ${selectedGroup?.pnr}` : `THANH TOAN ${selectedCustomer?.name} ${selectedCustomer?.pnr || ''}`
                    )} 
                    alt="VietQR" 
                    className="mx-auto w-48 h-48 rounded-lg shadow-sm border border-white"
                  />
                  <p className="text-[10px] text-slate-500 mt-2">Tự động cập nhật số tiền & nội dung</p>
                </div>
              )}

              {/* Action Button */}
              <button
                disabled={activeTab === 'pnr' ? !selectedGroup : !selectedCustomer}
                onClick={() => processPayment(activeTab === 'pnr' ? 'Gộp' : 'Lẻ')}
                className={`w-full py-4 rounded-xl font-bold text-lg shadow-lg transition-all flex items-center justify-center gap-2 ${
                  (activeTab === 'pnr' ? selectedGroup : selectedCustomer)
                  ? 'bg-indigo-600 hover:bg-indigo-700 text-white transform active:scale-[0.98]'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
                }`}
              >
                <CheckCircle2 size={22} />
                Xác nhận Thanh toán
              </button>
              
              <p className="text-center text-[10px] text-slate-400 mt-4 italic">
                Bằng việc xác nhận, hệ thống sẽ tự động in hóa đơn và cập nhật trạng thái khách hàng.
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* --- Invoice Modal --- */}
      {showInvoice && lastInvoice && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/60 backdrop-blur-sm">
          <div className="bg-white w-full max-w-md rounded-3xl shadow-2xl overflow-hidden animate-in fade-in zoom-in-95 duration-300">
            <div className="bg-indigo-600 p-6 text-white flex justify-between items-center">
              <div className="flex items-center gap-2">
                <Receipt size={24} />
                <h3 className="font-bold text-lg">Hóa đơn điện tử</h3>
              </div>
              <button onClick={() => setShowInvoice(false)} className="hover:bg-indigo-500 p-1 rounded-full transition-colors">
                <X size={20} />
              </button>
            </div>
            
            <div className="p-8 space-y-6" id="printable-receipt">
              <div className="text-center border-b border-slate-100 pb-6">
                <h2 className="text-xl font-black text-slate-800 uppercase tracking-widest">Nha Khoa Minh Sinh</h2>
                <p className="text-xs text-slate-500 mt-1">123 Đường ABC, Quận 1, TP. Hồ Chí Minh</p>
                <p className="text-xs text-slate-500">Hotline: 1900 1234</p>
              </div>

              <div className="space-y-2 text-sm">
                <div className="flex justify-between"><span className="text-slate-500">Mã giao dịch:</span> <span className="font-mono font-bold">{lastInvoice.id}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Thời gian:</span> <span>{lastInvoice.time}</span></div>
                <div className="flex justify-between"><span className="text-slate-500">Khách hàng:</span> <span className="font-bold">{lastInvoice.customerName}</span></div>
                {lastInvoice.pnr && <div className="flex justify-between"><span className="text-slate-500">Mã PNR:</span> <span className="font-mono">{lastInvoice.pnr}</span></div>}
                <div className="flex justify-between"><span className="text-slate-500">Hình thức:</span> <span>{lastInvoice.method}</span></div>
              </div>

              <div className="border-y border-slate-100 py-4 space-y-2">
                <p className="text-[10px] font-bold text-slate-400 uppercase mb-2">Chi tiết dịch vụ</p>
                {lastInvoice.type === 'Gộp' ? (
                  lastInvoice.details.customers.map((c: any) => (
                    <div key={c.id} className="text-sm">
                      <p className="font-semibold text-slate-700">{c.name}</p>
                      {c.services.map((s: any) => (
                        <div key={s.id} className="flex justify-between pl-2 text-slate-500 italic">
                          <span>- {s.name}</span>
                          <span>{s.price.toLocaleString('vi-VN')}</span>
                        </div>
                      ))}
                    </div>
                  ))
                ) : (
                  lastInvoice.details.services.map((s: any) => (
                    <div key={s.id} className="flex justify-between text-sm">
                      <span className="text-slate-700">{s.name}</span>
                      <span className="font-mono">{s.price.toLocaleString('vi-VN')}</span>
                    </div>
                  ))
                )}
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-xl font-black text-indigo-700">
                  <span>TỔNG TIỀN:</span>
                  <span>{lastInvoice.amount.toLocaleString('vi-VN')}đ</span>
                </div>
                <p className="text-center text-[10px] text-slate-400 italic mt-4">Cảm ơn quý khách đã tin tưởng Nha Khoa Minh Sinh!</p>
              </div>
            </div>

            <div className="p-6 bg-slate-50 flex gap-3">
              <button 
                onClick={() => window.print()}
                className="flex-1 bg-white border border-slate-200 hover:bg-slate-100 text-slate-700 py-3 rounded-xl font-bold flex items-center justify-center gap-2 transition-all"
              >
                <Printer size={18} /> In hóa đơn
              </button>
              <button 
                onClick={() => setShowInvoice(false)}
                className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-xl font-bold transition-all"
              >
                Hoàn tất
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx global>{`
        @media print {
          body * { visibility: hidden; }
          #printable-receipt, #printable-receipt * { visibility: visible; }
          #printable-receipt { position: absolute; left: 0; top: 0; width: 100%; }
        }
      `}</style>
    </div>
  );
}
