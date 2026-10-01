'use client';
import React, { useState, useEffect } from 'react';

// Danh sách 32 răng chuẩn FDI (4 Cung hàm)
const QUADRANT_1 = [18, 17, 16, 15, 14, 13, 12, 11]; // Hàm trên phải
const QUADRANT_2 = [21, 22, 23, 24, 25, 26, 27, 28]; // Hàm trên trái
const QUADRANT_3 = [48, 47, 46, 45, 44, 43, 42, 41]; // Hàm dưới phải
const QUADRANT_4 = [31, 32, 33, 34, 35, 36, 37, 38]; // Hàm dưới trái

export default function Odontogram({ customerId }) {
    // State quản lý Chế độ hiển thị
    const [mode, setMode] = useState('DIAGNOSIS'); // 'DIAGNOSIS' hoặc 'SERVICE'
    
    // State lưu bệnh lý (Chẩn đoán) - Load từ API PatientToothStatus
    const [toothConditions, setToothConditions] = useState({}); 
    
    // State lưu giỏ hàng dịch vụ (Phác đồ) - Sẽ đẩy về API Consultation
    const [cartServices, setCartServices] = useState([]);
    
    // Răng đang được chọn để thao tác
    const [activeTooth, setActiveTooth] = useState(null);

    // Bảng màu bệnh lý trực quan
    const CONDITION_COLORS = {
        'Normal': '#f1f5f9',     // Trống (Khỏe)
        'Decayed': '#ef4444',    // Sâu (Đỏ)
        'Missing': '#1f2937',    // Mất (Đen xám)
        'Crowned': '#3b82f6',    // Bọc sứ (Xanh dương)
    };

    // Hàm Click vào 1 chiếc răng
    const handleToothClick = (toothNum) => {
        setActiveTooth(toothNum);
    };

    // BÁC SĨ CHỌN BỆNH LÝ (Chế độ Chẩn đoán)
    const assignCondition = (condition) => {
        if (!activeTooth) return;
        setToothConditions(prev => ({ ...prev, [activeTooth]: condition }));
        setActiveTooth(null);
    };

    // BÁC SĨ CHỌN DỊCH VỤ (Chế độ Dịch vụ)
    const assignService = (serviceName, price) => {
        if (!activeTooth) return;
        setCartServices(prev => [...prev, { tooth: activeTooth, serviceName, price }]);
        setActiveTooth(null);
    };

    // Component vẽ từng chiếc răng
    const Tooth = ({ num }) => {
        const condition = toothConditions[num] || 'Normal';
        const color = CONDITION_COLORS[condition];
        const isSelected = activeTooth === num;
        const hasService = cartServices.some(s => s.tooth === num); // Đánh dấu răng đã có dịch vụ

        return (
            <div 
                onClick={() => handleToothClick(num)}
                className={`flex flex-col items-center justify-center w-10 h-12 rounded-t-lg border-2 cursor-pointer transition-all ${isSelected ? 'border-yellow-400 scale-110 shadow-lg z-10' : 'border-gray-300'}`}
                style={{ backgroundColor: color }}
            >
                <span className={`text-xs font-bold ${condition === 'Missing' ? 'text-white' : 'text-gray-700'}`}>{num}</span>
                {/* Chấm vàng báo hiệu răng này đã được chọn dịch vụ */}
                {hasService && <div className="w-2 h-2 bg-yellow-400 rounded-full mt-1"></div>}
            </div>
        );
    };

    return (
        <div className="p-6 bg-white rounded-xl shadow-sm border border-gray-100 max-w-5xl mx-auto">
            {/* Thanh điều hướng 2 Chế độ (Giống Flow bạn mô tả) */}
            <div className="flex gap-4 mb-8 border-b pb-4">
                <button 
                    onClick={() => setMode('DIAGNOSIS')}
                    className={`px-6 py-2 rounded-lg font-bold ${mode === 'DIAGNOSIS' ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-500 hover:bg-gray-200 transition-colors'}`}
                >
                    1. Chẩn đoán Bệnh lý (Tạo sơ đồ)
                </button>
                <button 
                    onClick={() => setMode('SERVICE')}
                    className={`px-6 py-2 rounded-lg font-bold ${mode === 'SERVICE' ? 'bg-emerald-600 text-white' : 'bg-gray-100 text-gray-500 hover:bg-gray-200 transition-colors'}`}
                >
                    2. Chỉ định Dịch vụ (Phác đồ)
                </button>
            </div>

            <div className="flex gap-8">
                {/* KHU VỰC TRÁI: BẢN ĐỒ RĂNG 32 CHIẾC */}
                <div className="flex-1 bg-gray-50 p-6 rounded-xl border border-gray-200">
                    <h3 className="text-center font-bold text-gray-700 mb-6">HÀM TRÊN</h3>
                    <div className="flex justify-center gap-2 mb-4">
                        {QUADRANT_1.map(n => <Tooth key={n} num={n} />)}
                        <div className="w-4 border-r-2 border-gray-300 mx-2"></div> {/* Rãnh giữa */}
                        {QUADRANT_2.map(n => <Tooth key={n} num={n} />)}
                    </div>
                    
                    <div className="flex justify-center gap-2 mt-8">
                        {QUADRANT_3.map(n => <Tooth key={n} num={n} />)}
                        <div className="w-4 border-r-2 border-gray-300 mx-2"></div> {/* Rãnh giữa */}
                        {QUADRANT_4.map(n => <Tooth key={n} num={n} />)}
                    </div>
                    <h3 className="text-center font-bold text-gray-700 mt-6">HÀM DƯỚI</h3>
                </div>

                {/* KHU VỰC PHẢI: BẢNG ĐIỀU KHIỂN DỰA THEO MODE */}
                <div className="w-80 bg-white p-4 rounded-xl border border-gray-200 shadow-inner">
                    {activeTooth ? (
                        <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
                            <h4 className="font-bold text-blue-800 mb-2">Đang thao tác Răng: {activeTooth}</h4>
                            
                            {/* NẾU ĐANG Ở BƯỚC 1: CHỌN BỆNH LÝ */}
                            {mode === 'DIAGNOSIS' && (
                                <div className="flex flex-col gap-2 mt-4">
                                    <button onClick={() => assignCondition('Normal')} className="p-2 bg-white border rounded hover:bg-gray-100 font-medium">Khỏe mạnh (Trắng)</button>
                                    <button onClick={() => assignCondition('Decayed')} className="p-2 bg-red-100 border border-red-300 text-red-700 rounded hover:bg-red-200 font-medium">Sâu răng (Đỏ)</button>
                                    <button onClick={() => assignCondition('Missing')} className="p-2 bg-gray-800 border border-gray-900 text-white rounded hover:bg-gray-700 font-medium">Đã mất (Đen)</button>
                                    <button onClick={() => assignCondition('Crowned')} className="p-2 bg-blue-100 border border-blue-300 text-blue-700 rounded hover:bg-blue-200 font-medium">Đã bọc sứ (Xanh)</button>
                                </div>
                            )}

                            {/* NẾU ĐANG Ở BƯỚC 2: CHỌN DỊCH VỤ */}
                            {mode === 'SERVICE' && (
                                <div className="flex flex-col gap-2 mt-4">
                                    <p className="text-sm text-gray-600 mb-2">Chỉ định dịch vụ cho Răng {activeTooth}:</p>
                                    <button onClick={() => assignService('Trám răng Composite', 300000)} className="p-2 bg-emerald-100 border border-emerald-300 text-emerald-800 rounded font-semibold transition-colors hover:bg-emerald-200">+ Trám răng</button>
                                    <button onClick={() => assignService('Bọc sứ Titan', 1500000)} className="p-2 bg-emerald-100 border border-emerald-300 text-emerald-800 rounded font-semibold transition-colors hover:bg-emerald-200">+ Bọc sứ Titan</button>
                                    <button onClick={() => assignService('Nhổ răng khôn', 1000000)} className="p-2 bg-emerald-100 border border-emerald-300 text-emerald-800 rounded font-semibold transition-colors hover:bg-emerald-200">+ Nhổ răng</button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="mb-6 p-4 bg-gray-50 rounded-lg text-center text-gray-500 border border-dashed border-gray-300">
                            👈 Hãy Click vào một chiếc răng bên trái để thao tác
                        </div>
                    )}

                    {/* HIỂN THỊ GIỎ HÀNG DỊCH VỤ DÙ ĐANG Ở MODE NÀO */}
                    <div className="border-t pt-4">
                        <h4 className="font-bold text-gray-800 mb-2">Danh sách Phác đồ:</h4>
                        {cartServices.length === 0 ? (
                            <p className="text-sm text-gray-500 italic">Chưa có dịch vụ nào.</p>
                        ) : (
                            <ul className="text-sm flex flex-col gap-2">
                                {cartServices.map((item, idx) => (
                                    <li key={idx} className="flex justify-between items-center p-2 bg-gray-50 border rounded">
                                        <span><span className="font-bold text-indigo-600">R{item.tooth}</span>: {item.serviceName}</span>
                                        <span className="font-bold text-red-600">{(item.price).toLocaleString()}đ</span>
                                    </li>
                                ))}
                            </ul>
                        )}
                        <button className="w-full mt-4 bg-blue-600 text-white font-bold py-3 rounded-lg shadow hover:bg-blue-700 transition-colors">
                            💾 LƯU BỆNH ÁN & PHÁC ĐỒ
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
