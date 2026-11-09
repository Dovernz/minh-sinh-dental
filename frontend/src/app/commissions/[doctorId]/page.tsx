'use client';
import { useState, useEffect, use } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';

type DetailData = {
    booking_id: number;
    date: string;
    customer: string;
    service: string;
    role: string;
    actual_price: number;
    commission: number;
};

export default function CommissionDetail({ params }: { params: Promise<{ doctorId: string }> }) {
    const searchParams = useSearchParams();
    const month = searchParams.get('month') || '';
    const [data, setData] = useState<DetailData[]>([]);
    const [loading, setLoading] = useState(true);
    
    const resolvedParams = use(params);
    const doctorId = Number(resolvedParams.doctorId);

    useEffect(() => {
        let url = `http://localhost:8000/api/reports/commissions/${doctorId}/`;
        if (month) {
            const [year, m] = month.split('-');
            const startDate = `${year}-${m}-01`;
            const endDate = new Date(Number(year), Number(m), 0).toISOString().split('T')[0];
            url += `?start_date=${startDate}&end_date=${endDate}`;
        }

        setLoading(true);
        fetch(url)
            .then(res => res.json())
            .then((resData: DetailData[]) => {
                // Sort by date desc
                const sorted = [...(resData || [])].sort((a, b) => {
                    const dateA = a.date ? new Date(a.date).getTime() : 0;
                    const dateB = b.date ? new Date(b.date).getTime() : 0;
                    return dateB - dateA;
                });
                
                setData(sorted);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [doctorId, month]);

    if (loading) return <div className="min-h-screen bg-gray-100 dark:bg-slate-950 text-gray-800 dark:text-slate-100 p-6">Đang tải dữ liệu...</div>;

    const total = data.reduce((sum, item) => sum + item.commission, 0);

    return (
        <main className="min-h-screen bg-gray-100 dark:bg-slate-950 p-6">
            <div className="max-w-4xl mx-auto bg-white dark:bg-slate-900 rounded-lg shadow dark:shadow-none border border-transparent dark:border-slate-800 p-6">
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h1 className="text-2xl font-bold text-gray-800 dark:text-slate-100">Chi tiết Hoa hồng</h1>
                        <p className="text-gray-600 dark:text-slate-400 mt-1">Bác sĩ: <span className="font-semibold text-gray-800 dark:text-slate-200">#{doctorId}</span> {month && `- Tháng ${month}`}</p>
                    </div>
                    <Link 
                        href="/commissions"
                        className="px-4 py-2 bg-gray-200 dark:bg-slate-800 hover:bg-gray-300 dark:hover:bg-slate-700 text-gray-800 dark:text-slate-200 rounded font-semibold text-sm transition"
                    >
                        Quay lại
                    </Link>
                </div>

                <div className="mb-4 p-4 bg-green-50 dark:bg-emerald-950/30 rounded-lg border border-green-100 dark:border-emerald-800/40 flex justify-between items-center">
                    <span className="font-semibold text-green-800 dark:text-emerald-300">Tổng cộng:</span>
                    <span className="text-xl font-bold text-green-700 dark:text-emerald-400">{total.toLocaleString('vi-VN')} ₫</span>
                </div>

                {data.length === 0 ? (
                    <p className="text-gray-500 dark:text-slate-400 italic text-center py-8">Không có dữ liệu chi tiết.</p>
                ) : (
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-gray-50 dark:bg-slate-800/60 border-b border-gray-200 dark:border-slate-700 text-gray-700 dark:text-slate-300">
                                <th className="p-3">Ngày</th>
                                <th className="p-3">Khách hàng</th>
                                <th className="p-3">Khám/Dịch vụ</th>
                                <th className="p-3">Vai trò</th>
                                <th className="p-3 text-right">Hoa hồng (VNĐ)</th>
                            </tr>
                        </thead>
                        <tbody>
                            {data.map((item, idx) => (
                                <tr key={idx} className="border-b border-gray-200 dark:border-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800/60 transition">
                                    <td className="p-3 text-gray-600 dark:text-slate-400">
                                        {item.date ? new Date(item.date).toLocaleString('vi-VN') : ''}
                                    </td>
                                    <td className="p-3 font-medium text-gray-900 dark:text-slate-100">{item.customer}</td>
                                    <td className="p-3 font-medium text-gray-800 dark:text-slate-200">{item.service}</td>
                                    <td className="p-3 text-gray-600 dark:text-slate-400">
                                        {item.role === 'Consulting' ? 'Tư vấn' : 'Thực hiện'}
                                    </td>
                                    <td className="p-3 text-right text-green-600 dark:text-emerald-400 font-semibold">
                                        {item.commission.toLocaleString('vi-VN')} ₫
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
        </main>
    );
}