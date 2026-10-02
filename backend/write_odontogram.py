odontogram_content = '''\'use client\';
import React, { useState } from \'react\';

const QUADRANT_1 = [18, 17, 16, 15, 14, 13, 12, 11];
const QUADRANT_2 = [21, 22, 23, 24, 25, 26, 27, 28];
const QUADRANT_3 = [48, 47, 46, 45, 44, 43, 42, 41];
const QUADRANT_4 = [31, 32, 33, 34, 35, 36, 37, 38];

type Condition = \'Normal\' | \'Decayed\' | \'Missing\' | \'Crowned\';
type ServiceItem = { tooth: number; serviceName: string; price: number };

const CONDITION_COLORS: Record<Condition, string> = {
    Normal: \'#f1f5f9\',
    Decayed: \'#ef4444\',
    Missing: \'#1f2937\',
    Crowned: \'#3b82f6\',
};

const CONDITION_LABELS: Record<Condition, string> = {
    Normal: \'Khoe manh (Trang)\',
    Decayed: \'Sau rang (Do)\',
    Missing: \'Da mat (Den)\',
    Crowned: \'Da boc su (Xanh)\',
};

export default function Odontogram({ customerId }: { customerId?: string | number }) {
    const [mode, setMode] = useState<\'DIAGNOSIS\' | \'SERVICE\'>(\'DIAGNOSIS\');
    const [toothConditions, setToothConditions] = useState<Record<number, Condition>>({});
    const [cartServices, setCartServices] = useState<ServiceItem[]>([]);
    const [activeTooth, setActiveTooth] = useState<number | null>(null);

    const handleToothClick = (toothNum: number) => setActiveTooth(toothNum);

    const assignCondition = (condition: Condition) => {
        if (!activeTooth) return;
        setToothConditions(prev => ({ ...prev, [activeTooth]: condition }));
        setActiveTooth(null);
    };

    const assignService = (serviceName: string, price: number) => {
        if (!activeTooth) return;
        setCartServices(prev => [...prev, { tooth: activeTooth, serviceName, price }]);
        setActiveTooth(null);
    };

    const Tooth = ({ num }: { num: number }) => {
        const condition = toothConditions[num] || \'Normal\';
        const color = CONDITION_COLORS[condition];
        const isSelected = activeTooth === num;
        const hasService = cartServices.some(s => s.tooth === num);
        return (
            <div
                onClick={() => handleToothClick(num)}
                className={`relative flex flex-col items-center justify-center w-10 h-12 rounded-t-lg border-2 cursor-pointer transition-all ${isSelected ? \'border-yellow-400 scale-110 shadow-lg z-10\' : \'border-gray-300 hover:border-blue-400\'}`}
                style={{ backgroundColor: color }}
            >
                <span className={`text-xs font-bold ${condition === \'Missing\' ? \'text-white\' : \'text-gray-700\'}`}>{num}</span>
                {hasService && <div className="absolute top-1 right-1 w-2 h-2 bg-yellow-400 rounded-full"></div>}
            </div>
        );
    };

    const total = cartServices.reduce((sum, s) => sum + s.price, 0);

    return (
        <div className="p-4 bg-white min-h-screen font-sans">
            <h2 className="text-xl font-bold text-gray-800 mb-4">So do Rang 32 chiec (FDI)</h2>
            <div className="flex gap-3 mb-6 border-b pb-4">
                <button onClick={() => setMode(\'DIAGNOSIS\')} className={`px-5 py-2 rounded-lg font-bold text-sm transition-colors ${mode === \'DIAGNOSIS\' ? \'bg-indigo-600 text-white shadow\' : \'bg-gray-100 text-gray-500 hover:bg-gray-200\'}`}>
                    1. Chan doan Benh ly
                </button>
                <button onClick={() => setMode(\'SERVICE\')} className={`px-5 py-2 rounded-lg font-bold text-sm transition-colors ${mode === \'SERVICE\' ? \'bg-emerald-600 text-white shadow\' : \'bg-gray-100 text-gray-500 hover:bg-gray-200\'}`}>
                    2. Chi dinh Dich vu
                </button>
            </div>

            <div className="flex gap-6">
                <div className="flex-1 bg-gray-50 p-4 rounded-xl border border-gray-200">
                    <p className="text-center text-sm font-semibold text-gray-500 mb-4 uppercase tracking-wide">Ham Tren</p>
                    <div className="flex justify-center items-end gap-1 mb-2">
                        {QUADRANT_1.map(n => <Tooth key={n} num={n} />)}
                        <div className="w-px h-12 bg-gray-400 mx-2"></div>
                        {QUADRANT_2.map(n => <Tooth key={n} num={n} />)}
                    </div>
                    <div className="border-t-2 border-dashed border-gray-400 my-4"></div>
                    <div className="flex justify-center items-start gap-1 mt-2">
                        {QUADRANT_3.map(n => <Tooth key={n} num={n} />)}
                        <div className="w-px h-12 bg-gray-400 mx-2"></div>
                        {QUADRANT_4.map(n => <Tooth key={n} num={n} />)}
                    </div>
                    <p className="text-center text-sm font-semibold text-gray-500 mt-4 uppercase tracking-wide">Ham Duoi</p>

                    <div className="flex gap-3 mt-6 justify-center flex-wrap">
                        {(Object.entries(CONDITION_COLORS) as [Condition, string][]).map(([k, v]) => (
                            <div key={k} className="flex items-center gap-1 text-xs text-gray-600">
                                <div className="w-4 h-4 rounded border border-gray-300" style={{ backgroundColor: v }}></div>
                                {CONDITION_LABELS[k]}
                            </div>
                        ))}
                        <div className="flex items-center gap-1 text-xs text-gray-600">
                            <div className="w-4 h-4 rounded bg-white border border-gray-300 flex items-center justify-center"><div className="w-2 h-2 rounded-full bg-yellow-400"></div></div>
                            Co dich vu
                        </div>
                    </div>
                </div>

                <div className="w-72 flex flex-col gap-4">
                    {activeTooth ? (
                        <div className="bg-blue-50 rounded-xl border border-blue-200 p-4">
                            <h4 className="font-bold text-blue-800 mb-3">Rang so: {activeTooth}</h4>
                            {mode === \'DIAGNOSIS\' ? (
                                <div className="flex flex-col gap-2">
                                    <p className="text-xs text-gray-500 mb-1">Chon tinh trang:</p>
                                    {(Object.keys(CONDITION_COLORS) as Condition[]).map(c => (
                                        <button key={c} onClick={() => assignCondition(c)}
                                            className="p-2 text-sm rounded border font-medium transition-colors text-left"
                                            style={{ backgroundColor: CONDITION_COLORS[c], borderColor: \'#d1d5db\', color: c === \'Missing\' ? \'white\' : \'#374151\' }}>
                                            {CONDITION_LABELS[c]}
                                        </button>
                                    ))}
                                </div>
                            ) : (
                                <div className="flex flex-col gap-2">
                                    <p className="text-xs text-gray-500 mb-1">Chi dinh dich vu cho rang {activeTooth}:</p>
                                    <button onClick={() => assignService(\'Tram rang Composite\', 300000)} className="p-2 text-sm bg-emerald-100 border border-emerald-300 text-emerald-800 rounded font-semibold hover:bg-emerald-200">+ Tram rang</button>
                                    <button onClick={() => assignService(\'Boc su Titan\', 1500000)} className="p-2 text-sm bg-emerald-100 border border-emerald-300 text-emerald-800 rounded font-semibold hover:bg-emerald-200">+ Boc su Titan</button>
                                    <button onClick={() => assignService(\'Nho rang khon\', 1000000)} className="p-2 text-sm bg-emerald-100 border border-emerald-300 text-emerald-800 rounded font-semibold hover:bg-emerald-200">+ Nho rang</button>
                                    <button onClick={() => assignService(\'Tay trang rang\', 500000)} className="p-2 text-sm bg-emerald-100 border border-emerald-300 text-emerald-800 rounded font-semibold hover:bg-emerald-200">+ Tay trang</button>
                                </div>
                            )}
                            <button onClick={() => setActiveTooth(null)} className="mt-3 text-xs text-gray-400 hover:text-gray-600 w-full text-center">Huy chon</button>
                        </div>
                    ) : (
                        <div className="bg-gray-50 rounded-xl border-2 border-dashed border-gray-300 p-6 text-center text-gray-400 text-sm">
                            Click vao mot chiec rang de thao tac
                        </div>
                    )}

                    <div className="bg-white rounded-xl border border-gray-200 p-4 flex-1">
                        <h4 className="font-bold text-gray-800 mb-3 pb-2 border-b">Phac do Dieu tri</h4>
                        {cartServices.length === 0 ? (
                            <p className="text-sm text-gray-400 italic text-center py-4">Chua co dich vu nao</p>
                        ) : (
                            <ul className="space-y-2 mb-4 max-h-48 overflow-y-auto">
                                {cartServices.map((item, idx) => (
                                    <li key={idx} className="flex justify-between items-start text-sm p-2 bg-gray-50 rounded border">
                                        <span><span className="font-bold text-indigo-600">R{item.tooth}</span>: {item.serviceName}</span>
                                        <span className="font-bold text-red-600 ml-2 whitespace-nowrap">{item.price.toLocaleString()}d</span>
                                    </li>
                                ))}
                            </ul>
                        )}
                        {cartServices.length > 0 && (
                            <div className="border-t pt-3">
                                <div className="flex justify-between font-bold text-sm mb-3">
                                    <span>Tong cong:</span>
                                    <span className="text-blue-700">{total.toLocaleString()}d</span>
                                </div>
                                <button className="w-full bg-blue-600 text-white font-bold py-2.5 rounded-lg shadow hover:bg-blue-700 transition-colors text-sm">
                                    Luu Benh an & Phac do
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
'''

with open('/app/src/components/Odontogram.tsx', 'w', encoding='utf-8') as f:
    f.write(odontogram_content)

print("Done writing Odontogram.tsx")
