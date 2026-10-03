'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Odontogram from '@/components/Odontogram';

function DentalChartContent() {
    const searchParams = useSearchParams();
    const customerId = searchParams.get('customerId') || 'preview';
    const customerName = searchParams.get('customerName') || '';
    
    const [view, setView] = useState<'list' | 'chart'>('list');
    const [charts, setCharts] = useState<any[]>([]);
    
    // Pass these to Odontogram
    const [selectedChartId, setSelectedChartId] = useState<number | null>(null);
    const [clonedFromId, setClonedFromId] = useState<number | null>(null);
    
    useEffect(() => {
        if (customerId && customerId !== 'preview') {
            // Fetch customer name
            // API fetch removed to prevent JSON error
                
            // Fetch charts
            fetchCharts();
        }
    }, [customerId]);

    const fetchCharts = () => {
        fetch(`http://localhost:8000/api/dental-charts/?customer_id=${customerId}`)
            .then(res => res.json())
            .then(data => {
                setCharts(data || []);
            })
            .catch(err => console.error(err));
    };

    const handleCreateNew = () => {
        setSelectedChartId(null);
        setClonedFromId(null);
        setView('chart');
    };

    const handleViewChart = (chartId: number) => {
        setSelectedChartId(chartId);
        setClonedFromId(null);
        setView('chart');
    };

    const handleContinueChart = (chartId: number) => {
        setSelectedChartId(null);
        setClonedFromId(chartId);
        setView('chart');
    };

    const handleBackToList = () => {
        fetchCharts();
        setView('list');
    };

    const customerDisplayName = customerName ? `Bệnh nhân: ${customerName}` : (customerId === 'preview' ? '#preview' : `Bệnh nhân: #${customerId}`);

    if (view === 'chart') {
        return (
            <main className="min-h-screen bg-white flex flex-col">
                <div className="p-4 bg-white border-b flex justify-between items-center shrink-0">
                    <h1 className="text-xl font-bold">{customerDisplayName}</h1>
                    <button 
                        onClick={handleBackToList}
                        className="px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded text-sm font-semibold"
                    >
                        Quay lại danh sách
                    </button>
                </div>
                <div className="flex-1 overflow-hidden">
                    <Odontogram 
                        customerId={customerId} 
                        initialChartId={selectedChartId}
                        initialClonedFromId={clonedFromId}
                        onSaved={fetchCharts}
                        onClose={handleBackToList}
                    />
                </div>
            </main>
        );
    }

    return (
        <main className="min-h-screen bg-white">
            <div className="w-full h-full p-4">
                <div className="flex justify-between items-center mb-6">
                    <h1 className="text-2xl font-bold text-gray-800">
                        Danh sách Sơ đồ răng - {customerDisplayName}
                    </h1>
                    <button 
                        onClick={handleCreateNew}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded font-semibold text-sm"
                    >
                        + Tạo sơ đồ mới tinh
                    </button>
                </div>

                {charts.length === 0 ? (
                    <p className="text-gray-500 italic text-center py-8">Chưa có sơ đồ nào.</p>
                ) : (
                    <table className="w-full text-left border-collapse">
                        <thead>
                            <tr className="bg-gray-50 border-b">
                                <th className="p-3">Sơ đồ số</th>
                                <th className="p-3">Ngày tạo</th>
                                <th className="p-3 text-right">Thao tác</th>
                            </tr>
                        </thead>
                        <tbody>
                            {charts.sort((a, b) => b.sequence_num - a.sequence_num).map(chart => (
                                <tr key={chart.id} className="border-b hover:bg-gray-50">
                                    <td className="p-3 font-semibold">Sơ đồ {chart.sequence_num}</td>
                                    <td className="p-3 text-gray-600">
                                        {new Date(chart.created_at).toLocaleString()}
                                    </td>
                                    <td className="p-3 text-right space-x-2">
                                        <button 
                                            onClick={() => handleViewChart(chart.id)}
                                            className="px-3 py-1.5 bg-indigo-50 text-indigo-600 hover:bg-indigo-100 rounded text-sm font-semibold"
                                        >
                                            Xem sơ đồ
                                        </button>
                                        <button 
                                            onClick={() => handleContinueChart(chart.id)}
                                            className="px-3 py-1.5 bg-green-50 text-green-600 hover:bg-green-100 rounded text-sm font-semibold"
                                        >
                                            Khám tiếp (Kế thừa)
                                        </button>
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

export default function DentalChartPage() {
    return (
        <Suspense fallback={<div>Loading...</div>}>
            <DentalChartContent />
        </Suspense>
    );
}
