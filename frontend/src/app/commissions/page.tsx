'use client';
import { useState, useEffect } from 'react';
import Link from 'next/link';

type OverviewData = {
    id: number;
    name: string;
    total_consulting: number;
    total_performing: number;
    total: number;
};

export default function CommissionsOverview() {
    const [data, setData] = useState<OverviewData[]>([]);
    const [loading, setLoading] = useState(true);
    const [month, setMonth] = useState(() => {
        const d = new Date();
        return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    });

    useEffect(() => {
        // Calculate start and end date of the month
        const [year, m] = month.split('-');
        const startDate = `${year}-${m}-01`;
        const endDate = new Date(Number(year), Number(m), 0).toISOString().split('T')[0];

        setLoading(true);
        fetch(`/api/reports/commissions/?start_date=${startDate}&end_date=${endDate}`)
            .then(res => res.json())
            .then(resData => {
                setData(resData || []);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, [month]);

    const doctorsList = [...data].sort((a, b) => b.total - a.total);

    if (loading) return <div className="min-h-screen bg-gray-100 dark:bg-slate-950 text-gray-800 dark:text-slate-100 p-6">Đang tải dữ liệu...</div>;

    return (
        <main className="min-h-screen bg-gray-100 dark:bg-slate-950 p-6">
            <div className="max-w-4xl mx-auto bg-white dark:bg-slate-900 rounded-lg shadow dark:shadow-none border border-transparent dark:border-slate-800 p-6">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-gray-800 dark:text-slate-100">Báo cáo Hoa hồng Bác sĩ</h1>
                    <div className="flex items-center gap-2">
                        <label className="text-sm font-semibold text-gray-700 dark:text-slate-300">Tháng:</label>
                        <input 
                            type="month" 
                            value={month} 
                            onChange={(e) => setMonth(e.target.value)} 
                            className="border border-gray-300 dark:border-slate-700 bg-white dark:bg-slate-800 text-gray-900 dark:text-slate-100 p-2 rounded text-sm outline-none focus:border-blue-500 dark:focus:border-blue-400 dark:[color-scheme:dark]"
                        />
                    </div>
                </div>

                {doctorsList.length === 0 ? (
                    <p className="text-gray-500 dark:text-slate-400 italic text-center py-8">Không có dữ liệu hoa hồng trong tháng này.</p>
                ) : (
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-gray-50 dark:bg-slate-800/60 border-b border-gray-200 dark:border-slate-700 text-gray-700 dark:text-slate-300">
                                <th className="p-3">Bác sĩ</th>
                                <th className="p-3 text-right">Tư vấn</th>
                                <th className="p-3 text-right">Thực hiện</th>
                                <th className="p-3 text-right">Tổng hoa hồng (VNĐ)</th>
                                <th className="p-3 text-right">Thao tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {doctorsList.map(doc => (
                                <tr key={doc.id} className="border-b border-gray-200 dark:border-slate-800 hover:bg-gray-50 dark:hover:bg-slate-800/60 transition">
                                    <td className="p-3 font-semibold text-gray-900 dark:text-slate-100">{doc.name}</td>
                                    <td className="p-3 text-right text-gray-600 dark:text-slate-400">
                                        {doc.total_consulting.toLocaleString('vi-VN')} ₫
                                    </td>
                                    <td className="p-3 text-right text-gray-600 dark:text-slate-400">
                                        {doc.total_performing.toLocaleString('vi-VN')} ₫
                                    </td>
                                    <td className="p-3 text-right text-green-600 dark:text-emerald-400 font-bold">
                                        {doc.total.toLocaleString('vi-VN')} ₫
                                    </td>
                                    <td className="p-3 text-right">
                                        <Link 
                                            href={`/commissions/${doc.id}?month=${month}`}
                                            className="inline-block px-4 py-2 bg-blue-50 dark:bg-blue-950/60 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/60 rounded text-sm font-semibold transition"
                                        >
                                            Xem chi tiết
                                        </Link>
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