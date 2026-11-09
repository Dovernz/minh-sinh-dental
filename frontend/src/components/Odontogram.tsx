'use client';

import React, { useState, useMemo, useEffect, useCallback } from 'react';

export type ConditionCode =
  | 'MV_R' | 'MV_L' | 'TL_R' | 'TL_O' | 'TL_L' | 'TL_I'
  | 'CRW' | 'VNR' | 'EN_O' | 'EN' | 'FRC' | 'CRK'
  | 'RN' | 'DN' | 'MCR' | 'INF' | 'PT_O' | 'PT'
  | 'ATR' | 'BRG' | 'RCN' | 'CF_O' | 'CF_R'
  | 'DST' | 'ATP' | 'MC' | 'CV' | 'VT'
  | 'RS' | 'CC' | 'NHO' | 'TKR' | 'ROOT'
  | 'NMP' | 'TUT' | 'TNC' | 'ATT' | 'EU' | 'GIC'
  | 'CO' | 'A' | 'DRF' | 'IM' | 'MT' | 'RD'
  | 'FCT' | 'RT_L' | 'RT_R' | 'TR' | 'LL' | 'DFT' | 'RST' | 'OCL' | 'NL';

export type Surface = 'M' | 'D' | 'B' | 'L' | 'O';

export type ToothData = {
  surfaces: Partial<Record<Surface, ConditionCode>>;
  wholeCondition?: ConditionCode;
};

interface ConditionItem {
  code: ConditionCode;
  label: string;
  color: string;
  badge?: string;
  bgColor?: string;
}

const CONDITIONS: ConditionItem[] = [
  // --- Di chuyển / Nghiêng ---
  { code: 'MV_R', label: 'Dịch Chuyển Phải',               color: '#ef4444' },
  { code: 'MV_L', label: 'Dịch Chuyển Trái',               color: '#ef4444' },
  { code: 'TL_R', label: 'Nghiêng Phải',                   color: '#ef4444' },
  { code: 'TL_O', label: 'Nghiêng Ra Ngoài',               color: '#ef4444' },
  { code: 'TL_L', label: 'Nghiêng Trái',                   color: '#ef4444' },
  { code: 'TL_I', label: 'Nghiêng Trong',                  color: '#ef4444' },
  // --- Phục hình ---
  { code: 'CRW', label: 'Mão Răng',                        color: '#3b82f6', badge: 'MR',  bgColor: '#3b82f6' },
  { code: 'VNR', label: 'Veneer',                          color: '#10b981', badge: 'VN',  bgColor: '#10b981' },
  { code: 'EN_O', label: 'Nội Nha PK Khác',               color: '#60a5fa', badge: 'NN',  bgColor: '#60a5fa' },
  { code: 'EN',  label: 'Nội Nha PK',                     color: '#ef4444', badge: 'NN',  bgColor: '#ef4444' },
  { code: 'FRC', label: 'Gãy Răng',                        color: '#6b7280' },
  { code: 'CRK', label: 'Nứt Răng',                        color: '#3b82f6' },
  // --- Tình trạng răng ---
  { code: 'RN',  label: 'Răng Ngầm',                       color: '#ffffff', badge: 'RN',  bgColor: '#dc2626' },
  { code: 'DN',  label: 'Răng Đã Nhổ',                     color: '#ffffff', badge: 'DN',  bgColor: '#dc2626' },
  { code: 'MCR', label: 'Mòn Cổ Răng',                     color: '#f87171' },
  { code: 'INF', label: 'Nhiễm Trùng',                     color: '#ef4444' },
  { code: 'PT_O', label: 'Chốt PK Khác',                  color: '#3b82f6' },
  { code: 'PT',  label: 'Chốt PK',                        color: '#ef4444' },
  { code: 'ATR', label: 'Mòn Răng',                        color: '#9ca3af' },
  { code: 'BRG', label: 'Cầu Răng',                       color: '#2563eb', badge: 'CR',  bgColor: '#2563eb' },
  { code: 'RCN', label: 'Còn Chân Răng',                   color: '#dc2626' },
  { code: 'CF_O', label: 'Trám Cổ Răng PK Khác',          color: '#93c5fd' },
  { code: 'CF_R', label: 'Trám Cổ Răng Sâu Tái Phát',     color: '#fca5a5' },
  { code: 'DST', label: 'Răng Thưa',                      color: '#9ca3af' },
  { code: 'ATP', label: 'Mòn Lộ Tủy',                     color: '#ef4444' },
  // --- Bệnh lý vôi/nhú ---
  { code: 'MC',  label: 'MCR (Mòn Cổ Răng)',              color: '#ffffff', badge: 'MC',  bgColor: '#2563eb' },
  { code: 'CV',  label: 'Cao Vôi Răng',                   color: '#ffffff', badge: 'CV',  bgColor: '#3b82f6' },
  { code: 'VT',  label: 'Viêm Tủy Răng',                  color: '#ffffff', badge: 'VT',  bgColor: '#4338ca' },
  { code: 'RS',  label: 'Bọc Răng Sứ',                    color: '#ffffff', badge: 'RS',  bgColor: '#2563eb' },
  { code: 'CC',  label: 'Răng Mọc Chen Chúc',             color: '#ffffff', badge: 'CC',  bgColor: '#3b82f6' },
  { code: 'NHO', label: 'Răng Cần Nhổ',                   color: '#ef4444' },
  { code: 'TKR', label: 'Thừa Kẽ Răng',                   color: '#9ca3af' },
  { code: 'ROOT', label: 'Chân Răng',                     color: '#dc2626' },
  { code: 'NMP', label: 'Có Núm Phụ',                     color: '#9ca3af' },
  { code: 'TUT', label: 'Tụt Nướu',                       color: '#f87171' },
  { code: 'TNC', label: 'Túi Nha Chu',                    color: '#1f2937' },
  { code: 'ATT', label: 'Lưu ý',                          color: '#ef4444' },
  // --- Vật liệu trám ---
  { code: 'EU',  label: 'Eugenat',                        color: '#ffffff', badge: 'EU',  bgColor: '#0d9488' },
  { code: 'GIC', label: 'GIC',                            color: '#ffffff', badge: 'GIC', bgColor: '#7c3aed' },
  { code: 'CO',  label: 'Composite',                      color: '#ffffff', badge: 'CO',  bgColor: '#2563eb' },
  { code: 'A',   label: 'Amalgam',                        color: '#ffffff', badge: 'A',   bgColor: '#ec4899' },
  // --- Khác ---
  { code: 'DRF', label: 'Di Chuyển',                      color: '#facc15' },
  { code: 'IM',  label: 'Implant',                        color: '#6b7280' },
  { code: 'MT',  label: 'Mất Răng',                       color: '#4b5563' },
  { code: 'RD',  label: 'Răng Dư',                        color: '#9ca3af' },
  { code: 'FCT', label: 'Mất Dần',                        color: '#6b7280' },
  { code: 'RT_L', label: 'Xoay Trái',                    color: '#22c55e' },
  { code: 'RT_R', label: 'Xoay Phải',                    color: '#22c55e' },
  { code: 'TR',  label: 'Thiếu Răng',                     color: '#ef4444' },
  { code: 'LL',  label: 'Lung Lay',                       color: '#ffffff', badge: 'LL',  bgColor: '#2563eb' },
  { code: 'DFT', label: 'Răng Khiếm Khuyết',             color: '#fbbf24' },
  { code: 'RST', label: 'Đã Phục Hồi',                   color: '#3b82f6' },
  { code: 'OCL', label: 'Mặt Nhai',                       color: '#9ca3af' },
];

const CONDITION_COLOR_MAP: Record<ConditionCode, string> = CONDITIONS.reduce(
  (acc, c) => ({ ...acc, [c.code]: c.color }),
  {} as Record<ConditionCode, string>
);

const Q1 = [18, 17, 16, 15, 14, 13, 12, 11];
const Q2 = [21, 22, 23, 24, 25, 26, 27, 28];
const Q3 = [48, 47, 46, 45, 44, 43, 42, 41];
const Q4 = [31, 32, 33, 34, 35, 36, 37, 38];
const ALL_TEETH = [...Q1, ...Q2, ...Q3, ...Q4];

const getToothWidth = (num: number): number => {
  const lastDigit = num % 10;
  if (lastDigit === 6 || lastDigit === 7 || lastDigit === 8) {
    return 64; // molars (enlarged 2x)
  }
  if (lastDigit === 1 || lastDigit === 2 || lastDigit === 3) {
    return 40; // incisors / canines (enlarged 2x)
  }
  return 48; // premolars (enlarged 2x)
};

interface SurfaceCircleProps {
  surfaces: Partial<Record<Surface, ConditionCode>>;
  onSurfaceClick: (surface: Surface) => void;
}

function SurfaceCircle({ surfaces, onSurfaceClick }: SurfaceCircleProps) {
  const getFill = (s: Surface) => {
    const code = surfaces[s];
    if (!code) return '#ffffff';
    return CONDITION_COLOR_MAP[code] || '#3b82f6';
  };

  const getTextColor = (s: Surface) => {
    const code = surfaces[s];
    if (!code) return '#64748b';
    return code === 'NL' ? '#065f46' : '#ffffff';
  };

  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 28 28"
      className="overflow-visible select-none shrink-0"
    >
      {/* Top segment: O (Occlusal) */}
      <path
        d="M 10.82 10.82 L 5.51 5.51 A 12 12 0 0 1 22.49 5.51 L 17.18 10.82 A 4.5 4.5 0 0 0 10.82 10.82 Z"
        fill={getFill('O')}
        stroke="#94a3b8"
        strokeWidth="0.8"
        className="cursor-pointer hover:opacity-80 transition-opacity"
        onClick={(e) => {
          e.stopPropagation();
          onSurfaceClick('O');
        }}
      >
        <title>O - Occlusal</title>
      </path>

      {/* Right segment: D (Distal) */}
      <path
        d="M 17.18 10.82 L 22.49 5.51 A 12 12 0 0 1 22.49 22.49 L 17.18 17.18 A 4.5 4.5 0 0 0 17.18 10.82 Z"
        fill={getFill('D')}
        stroke="#94a3b8"
        strokeWidth="0.8"
        className="cursor-pointer hover:opacity-80 transition-opacity"
        onClick={(e) => {
          e.stopPropagation();
          onSurfaceClick('D');
        }}
      >
        <title>D - Distal</title>
      </path>

      {/* Bottom segment: L (Lingual) */}
      <path
        d="M 17.18 17.18 L 22.49 22.49 A 12 12 0 0 1 5.51 22.49 L 10.82 17.18 A 4.5 4.5 0 0 0 17.18 17.18 Z"
        fill={getFill('L')}
        stroke="#94a3b8"
        strokeWidth="0.8"
        className="cursor-pointer hover:opacity-80 transition-opacity"
        onClick={(e) => {
          e.stopPropagation();
          onSurfaceClick('L');
        }}
      >
        <title>L - Lingual</title>
      </path>

      {/* Left segment: M (Mesial) */}
      <path
        d="M 10.82 17.18 L 5.51 22.49 A 12 12 0 0 1 5.51 5.51 L 10.82 10.82 A 4.5 4.5 0 0 0 10.82 17.18 Z"
        fill={getFill('M')}
        stroke="#94a3b8"
        strokeWidth="0.8"
        className="cursor-pointer hover:opacity-80 transition-opacity"
        onClick={(e) => {
          e.stopPropagation();
          onSurfaceClick('M');
        }}
      >
        <title>M - Mesial</title>
      </path>

      {/* Center circle: B (Buccal) */}
      <circle
        cx="14"
        cy="14"
        r="4.5"
        fill={getFill('B')}
        stroke="#94a3b8"
        strokeWidth="0.8"
        className="cursor-pointer hover:opacity-80 transition-opacity"
        onClick={(e) => {
          e.stopPropagation();
          onSurfaceClick('B');
        }}
      >
        <title>B - Buccal</title>
      </circle>

      {/* Text labels on surfaces */}
      <text x="14" y="8" textAnchor="middle" fontSize="5" fontWeight="bold" fill={getTextColor('O')} pointerEvents="none">
        O
      </text>
      <text x="20" y="15.5" textAnchor="middle" fontSize="5" fontWeight="bold" fill={getTextColor('D')} pointerEvents="none">
        D
      </text>
      <text x="14" y="22.5" textAnchor="middle" fontSize="5" fontWeight="bold" fill={getTextColor('L')} pointerEvents="none">
        L
      </text>
      <text x="8" y="15.5" textAnchor="middle" fontSize="5" fontWeight="bold" fill={getTextColor('M')} pointerEvents="none">
        M
      </text>
      <text x="14" y="15.5" textAnchor="middle" fontSize="4.5" fontWeight="bold" fill={getTextColor('B')} pointerEvents="none">
        B
      </text>
    </svg>
  );
}

// SVG Anatomy Paths - 10 tooth types (5 upper + 5 lower) per FDI standard
const TOOTH_PATHS: Record<string, string> = {
  // Upper jaw
  upperCentral:  'M 6 20 C 6 8, 9 2, 12 2 C 15 2, 18 8, 18 20 C 20 30, 19 38, 12 38 C 5 38, 4 30, 6 20 Z',
  upperLateral:  'M 7 18 C 7 7, 10 2, 12 2 C 14 2, 17 7, 17 18 C 19 28, 18 36, 12 36 C 6 36, 5 28, 7 18 Z',
  upperCanine:   'M 7 16 C 7 6, 11 2, 12 2 C 13 2, 17 6, 17 16 C 19 26, 15 40, 12 41 C 9 40, 5 26, 7 16 Z',
  upperPremolar: 'M 5 16 C 5 6, 9 2, 12 2 C 15 2, 19 6, 19 16 C 22 24, 20 34, 16 36 C 14 36, 12 33, 12 33 C 12 33, 10 36, 8 36 C 4 34, 2 24, 5 16 Z',
  upperMolar:    'M 3 18 C 3 7, 7 2, 9 3 C 10 3, 11 8, 12 9 C 13 8, 14 3, 15 3 C 17 2, 21 7, 21 18 C 24 26, 22 36, 18 37 C 16 37, 13 33, 12 33 C 11 33, 8 37, 6 37 C 2 36, 0 26, 3 18 Z',
  // Lower jaw (mirrored anatomy)
  lowerCentral:  'M 8 18 C 8 6, 10 2, 12 2 C 14 2, 16 6, 16 18 C 17 28, 16 36, 12 36 C 8 36, 7 28, 8 18 Z',
  lowerLateral:  'M 7 18 C 7 7, 10 2, 12 2 C 14 2, 17 7, 17 18 C 18 28, 17 36, 12 36 C 7 36, 6 28, 7 18 Z',
  lowerCanine:   'M 7 16 C 7 6, 11 2, 12 2 C 13 2, 17 6, 17 16 C 19 26, 16 38, 12 39 C 8 38, 5 26, 7 16 Z',
  lowerPremolar: 'M 6 16 C 6 6, 9 2, 12 2 C 15 2, 18 6, 18 16 C 21 23, 20 32, 16 34 C 14 34, 12 31, 12 31 C 12 31, 10 34, 8 34 C 4 32, 3 23, 6 16 Z',
  lowerMolar:    'M 4 18 C 4 7, 8 2, 10 2 C 11 2, 12 9, 12 9 C 12 9, 13 2, 14 2 C 16 2, 20 7, 20 18 C 23 26, 22 36, 18 37 C 16 37, 13 33, 12 33 C 11 33, 8 37, 6 37 C 2 36, 1 26, 4 18 Z',
};

function getToothPath(num: number): string {
  // Upper jaw: Q1 (11-18) + Q2 (21-28)
  const d = num % 10;
  const isUpper = num >= 11 && num <= 28;
  if (isUpper) {
    if (d === 1) return TOOTH_PATHS.upperCentral;
    if (d === 2) return TOOTH_PATHS.upperLateral;
    if (d === 3) return TOOTH_PATHS.upperCanine;
    if (d === 4 || d === 5) return TOOTH_PATHS.upperPremolar;
    return TOOTH_PATHS.upperMolar; // 6,7,8
  } else {
    // Lower jaw: Q3 (31-38) + Q4 (41-48)
    if (d === 1) return TOOTH_PATHS.lowerCentral;
    if (d === 2) return TOOTH_PATHS.lowerLateral;
    if (d === 3) return TOOTH_PATHS.lowerCanine;
    if (d === 4 || d === 5) return TOOTH_PATHS.lowerPremolar;
    return TOOTH_PATHS.lowerMolar; // 6,7,8
  }
}

interface ToothSvgProps {
  width: number;
  height: number;
  toothNum: number;
  data: ToothData;
  isSelected: boolean;
}

function ToothSvg({ width, height, toothNum, data, isSelected }: ToothSvgProps) {
  const isMissing = data.wholeCondition === 'MT' || data.wholeCondition === 'DN';
  const condObj = data.wholeCondition ? CONDITIONS.find((c) => c.code === data.wholeCondition) : null;

  // Tooth fill: use condition color tinted, or white for normal
  let fillColor = '#ffffff';
  let strokeColor = isSelected ? '#2563eb' : '#94a3b8';
  let strokeWidth = isSelected ? '1.8' : '1';
  if (condObj && !isMissing) {
    // Soften condition color for fill (add transparency via opacity)
    fillColor = condObj.bgColor ? condObj.bgColor + '55' : condObj.color + '40';
  }
  if (isMissing) { fillColor = '#f1f5f9'; strokeColor = '#cbd5e1'; }

  const path = getToothPath(toothNum);
  const isUpper = toothNum >= 11 && toothNum <= 28;

  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 24 44"
      className="overflow-visible select-none"
      style={{ transform: isUpper ? 'none' : 'scaleY(-1)' }}
    >
      {/* Anatomical tooth outline */}
      <path
        d={path}
        fill={fillColor}
        stroke={strokeColor}
        strokeWidth={strokeWidth}
        strokeLinejoin="round"
        className="transition-colors duration-200"
      />
      {/* Condition badge text inside tooth */}
      {data.wholeCondition && !isMissing && (
        <text
          x="12"
          y="24"
          textAnchor="middle"
          fontSize="7"
          fontWeight="bold"
          fill={condObj?.bgColor ? '#ffffff' : '#1e293b'}
          style={{ transform: isUpper ? 'none' : 'scaleY(-1) translateY(-48px)' }}
        >
          {condObj?.badge || data.wholeCondition}
        </text>
      )}
      {/* Red X for missing tooth */}
      {isMissing && (
        <g stroke="#ef4444" strokeWidth="2" strokeLinecap="round">
          <line x1="5" y1="14" x2="19" y2="34" />
          <line x1="19" y1="14" x2="5" y2="34" />
        </g>
      )}
      {/* Crack line */}
      {data.wholeCondition === 'CRK' && (
        <path d="M 8 18 L 11 24 L 14 20 L 18 28" stroke="#3b82f6" fill="transparent" strokeWidth="1.5" strokeLinecap="round" />
      )}
    </svg>
  );
}

export default function Odontogram({ 
  customerId, 
  initialChartId, 
  initialClonedFromId,
  onSaved,
  onClose
}: { 
  customerId?: string | number;
  initialChartId?: number | null;
  initialClonedFromId?: number | null;
  onSaved?: () => void;
  onClose?: () => void;
}) {
  const [activeCondition, setActiveCondition] = useState<ConditionCode | null>(null);
  const [teeth, setTeeth] = useState<Record<number, ToothData>>({});
  const [selectedTooth, setSelectedTooth] = useState<number | null>(null);
  const [activeTab, setActiveTab] = useState<'detail' | 'condition'>('detail');
  const [searchQuery, setSearchQuery] = useState('');

  // Table rows for detail tab
  const [toothDetails, setToothDetails] = useState<
    Array<{ toothNum: number; loai: 'P' | 'N' | ''; dieuTri: string; ghiChu: string }>
  >([]);
  const [conditionNotes, setConditionNotes] = useState<Record<string, { phanLoai: string; dieuTri: string; ghiChu: string }>>({});

  // 4 textareas state
  const [ghiChu, setGhiChu] = useState('');
  const [canLamSang, setCanLamSang] = useState('');
  const [chanDoan, setChanDoan] = useState('');
  const [chiDinhDieuTri, setChiDinhDieuTri] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState('');

  const [charts, setCharts] = useState<any[]>([]);
  const [currentChartId, setCurrentChartId] = useState<number | null>(null);
  const [isReadOnly, setIsReadOnly] = useState(false);
  const [clonedFromId, setClonedFromId] = useState<number | null>(null);

  const API_BASE = '';

  useEffect(() => {
    if (!customerId) return;
    fetch(`${API_BASE}/api/dental-charts/?customer_id=${customerId}`)
      .then((r) => r.json())
      .then((data: any[]) => {
        setCharts(data);
        if (initialChartId) {
          const chart = data.find((c: any) => c.id === initialChartId);
          if (chart) {
            loadChartData(chart, true, null);
          }
        } else if (initialClonedFromId) {
          const chart = data.find((c: any) => c.id === initialClonedFromId);
          if (chart) {
            loadChartData(chart, false, initialClonedFromId);
          }
        } else {
          handleCreateNew();
        }
      })
      .catch(() => {});
  }, [customerId, initialChartId, initialClonedFromId]);

  const loadChartData = (chart: any, readOnly: boolean = true, clonedId: number | null = null) => {
    setCurrentChartId(readOnly ? chart.id : null);
    setIsReadOnly(readOnly);
    setClonedFromId(readOnly ? chart.cloned_from || null : clonedId);
    
    if (chart.tooth_data) {
      setTeeth(chart.tooth_data.teeth || {});
      setToothDetails(chart.tooth_data.details || []);
      setConditionNotes(chart.tooth_data.conditionNotes || {});
    } else {
      setTeeth({});
      setToothDetails([]);
      setConditionNotes({});
    }

    if (chart.notes_data) {
      setGhiChu(chart.notes_data.ghiChu || '');
      setCanLamSang(chart.notes_data.canLamSang || '');
      setChanDoan(chart.notes_data.chanDoan || '');
      setChiDinhDieuTri(chart.notes_data.chiDinhDieuTri || '');
    } else {
      setGhiChu('');
      setCanLamSang('');
      setChanDoan('');
      setChiDinhDieuTri('');
    }
  };

  const handleCreateNew = () => {
    setCurrentChartId(null);
    setIsReadOnly(false);
    setClonedFromId(null);
    setTeeth({});
    setToothDetails([]);
    setConditionNotes({});
    setGhiChu('');
    setCanLamSang('');
    setChanDoan('');
    setChiDinhDieuTri('');
  };

  const handleContinue = () => {
    setClonedFromId(currentChartId);
    setCurrentChartId(null);
    setIsReadOnly(false);
  };

  const handleSave = useCallback(async () => {
    if (!customerId) { setSaveMsg('Không có customerId'); return; }
    setIsSaving(true);
    setSaveMsg('');
    try {
      const payload = {
        customer: customerId,
        cloned_from: clonedFromId,
        tooth_data: { teeth, details: toothDetails, conditionNotes },
        notes_data: { ghiChu, canLamSang, chanDoan, chiDinhDieuTri }
      };
      
      const res = await fetch(`${API_BASE}/api/dental-charts/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const newChart = await res.json();
        setCharts((prev) => [...prev, newChart]);
        loadChartData(newChart, true, null);
        setSaveMsg('Đã lưu!');
        if (onSaved) onSaved();
      } else {
        setSaveMsg('Lưu thất bại!');
      }
    } catch {
      setSaveMsg('Lưu thất bại!');
    } finally {
      setIsSaving(false);
    }
  }, [customerId, toothDetails, conditionNotes, teeth, ghiChu, canLamSang, chanDoan, chiDinhDieuTri, clonedFromId]);

  // Filtered conditions for search input
  const filteredConditions = useMemo(() => {
    if (!searchQuery.trim()) return CONDITIONS;
    const q = searchQuery.toLowerCase().trim();
    return CONDITIONS.filter(
      (c) => c.label.toLowerCase().includes(q) || c.code.toLowerCase().includes(q)
    );
  }, [searchQuery]);

  // Click on tooth wrapper
  const handleToothClick = (toothNum: number) => {
    if (isReadOnly) return;
    if (activeCondition) {
      setTeeth((prev) => {
        const current = prev[toothNum] || { surfaces: {} };
        const newWhole = current.wholeCondition === activeCondition ? undefined : activeCondition;
        return {
          ...prev,
          [toothNum]: { ...current, wholeCondition: newWhole },
        };
      });
    } else {
      setSelectedTooth((prev) => (prev === toothNum ? null : toothNum));
      setToothDetails((prev) => {
        if (prev.some((d) => d.toothNum === toothNum)) return prev;
        return [...prev, { toothNum, loai: '', dieuTri: '', ghiChu: '' }];
      });
    }
  };

  // Click on surface segment
  const handleSurfaceClick = (toothNum: number, surface: Surface) => {
    if (isReadOnly) return;
    if (!activeCondition) return;
    setTeeth((prev) => {
      const current = prev[toothNum] || { surfaces: {} };
      const currentCond = current.surfaces[surface];
      const newSurfaces = { ...current.surfaces };
      if (currentCond === activeCondition) {
        delete newSurfaces[surface];
      } else {
        newSurfaces[surface] = activeCondition;
      }
      return {
        ...prev,
        [toothNum]: { ...current, surfaces: newSurfaces },
      };
    });
  };

  // Details tab actions
  const handleAddDetailRow = (toothNum?: number) => {
    if (isReadOnly) return;
    const targetTooth =
      toothNum ||
      selectedTooth ||
      ALL_TEETH.find((n) => !toothDetails.some((d) => d.toothNum === n)) ||
      11;
    setToothDetails((prev) => [
      ...prev,
      { toothNum: targetTooth, loai: '', dieuTri: '', ghiChu: '' },
    ]);
  };

  const handleUpdateDetail = (
    index: number,
    field: 'toothNum' | 'loai' | 'dieuTri' | 'ghiChu',
    value: any
  ) => {
    if (isReadOnly) return;
    setToothDetails((prev) => {
      const updated = [...prev];
      updated[index] = { ...updated[index], [field]: value };
      return updated;
    });
  };

  const handleDeleteDetail = (index: number) => {
    if (isReadOnly) return;
    setToothDetails((prev) => prev.filter((_, i) => i !== index));
  };

  // Flattened condition rows for Condition Tab
  const conditionRows = useMemo(() => {
    const rows: Array<{
      toothNum: number;
      surface: string;
      surfaceKey?: Surface;
      isWhole: boolean;
      code: ConditionCode;
      label: string;
      color: string;
    }> = [];

    const surfaceNameMap: Record<Surface, string> = {
      M: 'Mặt Gần (M)',
      D: 'Mặt Xa (D)',
      B: 'Mặt Ngoài (B)',
      L: 'Mặt Trong (L)',
      O: 'Mặt Nhai (O)',
    };

    Object.entries(teeth).forEach(([numStr, data]) => {
      const toothNum = parseInt(numStr, 10);
      if (data.wholeCondition) {
        const condObj = CONDITIONS.find((c) => c.code === data.wholeCondition);
        rows.push({
          toothNum,
          surface: 'Toàn bộ răng',
          isWhole: true,
          code: data.wholeCondition,
          label: condObj?.label || data.wholeCondition,
          color: condObj?.color || '#3b82f6',
        });
      }
      if (data.surfaces) {
        Object.entries(data.surfaces).forEach(([surf, code]) => {
          if (code) {
            const condObj = CONDITIONS.find((c) => c.code === code);
            rows.push({
              toothNum,
              surface: surfaceNameMap[surf as Surface] || surf,
              surfaceKey: surf as Surface,
              isWhole: false,
              code,
              label: condObj?.label || code,
              color: condObj?.color || '#3b82f6',
            });
          }
        });
      }
    });

    return rows.sort((a, b) => a.toothNum - b.toothNum);
  }, [teeth]);

  const handleRemoveCondition = (row: (typeof conditionRows)[0]) => {
    if (isReadOnly) return;
    const rowKey = `${row.toothNum}_${row.isWhole ? 'whole' : row.surfaceKey}`;
    
    setTeeth((prev) => {
      const current = prev[row.toothNum];
      if (!current) return prev;
      if (row.isWhole) {
        const { wholeCondition, ...rest } = current;
        return { ...prev, [row.toothNum]: rest };
      } else if (row.surfaceKey) {
        const newSurfaces = { ...current.surfaces };
        delete newSurfaces[row.surfaceKey];
        return { ...prev, [row.toothNum]: { ...current, surfaces: newSurfaces } };
      }
      return prev;
    });

    setConditionNotes((prev) => {
      const updated = { ...prev };
      delete updated[rowKey];
      return updated;
    });
  };

  // Reset form handler
    const handleReset = () => {
    if (window.confirm('Bạn có chắc chắn muốn đóng? (Những dữ liệu chưa Lưu sẽ bị mất)')) {
      if (onClose) {
        onClose();
      } else {
        setTeeth({});
        setConditionNotes({});
        setGhiChu('');
        setCanLamSang('');
        setChanDoan('');
        setChiDinhDieuTri('');
        setToothDetails([]);
        setSelectedTooth(null);
        setActiveCondition(null);
      }
    }
  };

  // Single tooth renderer
  const renderTooth = (toothNum: number) => {
    const toothData = teeth[toothNum] || { surfaces: {} };
    const isSelected = selectedTooth === toothNum;
    const width = getToothWidth(toothNum);

    return (
      <div
        key={toothNum}
        onClick={() => handleToothClick(toothNum)}
        className={`flex flex-col items-center p-1.5 rounded-lg cursor-pointer transition-all ${
          isSelected
            ? 'bg-blue-50 ring-2 ring-blue-500 shadow-sm'
            : 'hover:bg-gray-100'
        }`}
        style={{ minWidth: `${width + 8}px` }}
      >
        {/* Tooth number */}
        <span
          className={`text-xs font-bold mb-1 select-none ${
            isSelected ? 'text-blue-600' : 'text-gray-700'
          }`}
        >
          {toothNum}
        </span>

        {/* 5-surface circle */}
        <div className="mb-1">
          <SurfaceCircle
            surfaces={toothData.surfaces}
            onSurfaceClick={(surface) => handleSurfaceClick(toothNum, surface)}
          />
        </div>

        {/* Tooth SVG */}
        <ToothSvg
          width={width}
          height={80}
          toothNum={toothNum}
          data={toothData}
          isSelected={isSelected}
        />
      </div>
    );
  };

  return (
    <div className="flex flex-row bg-white w-full overflow-hidden text-gray-800 h-screen">
      {/* LEFT SIDEBAR (w-72) */}
      {!isReadOnly && (
        <aside className="w-72 shrink-0 bg-white border-r border-gray-200 flex flex-col p-4 print:hidden overflow-hidden h-screen">
          <div className="mb-4 flex-shrink-0">
            <h2 className="text-base font-bold text-gray-800 uppercase tracking-wide">
              Tình trạng răng
            </h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Bệnh lý răng người trưởng thành và trẻ em
            </p>
          </div>

          {/* Search input */}
          <div className="mb-3">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Tìm kiếm bệnh lý..."
              className="w-full px-3 py-2 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Active condition indicator */}
          {activeCondition && (
            <div className="mb-3 p-2 bg-blue-50 border border-blue-200 rounded-lg flex items-center justify-between text-xs">
              <div className="flex items-center gap-1.5 overflow-hidden">
                <span className="font-semibold text-blue-800 shrink-0">Đang chọn:</span>
                <span
                  className="px-1.5 py-0.5 rounded text-[10px] font-bold shrink-0"
                  style={{
                    backgroundColor:
                      CONDITIONS.find((c) => c.code === activeCondition)?.color || '#3b82f6',
                    color: activeCondition === 'NL' ? '#065f46' : '#ffffff',
                  }}
                >
                  {activeCondition}
                </span>
                <span className="text-blue-900 truncate">
                  {CONDITIONS.find((c) => c.code === activeCondition)?.label}
                </span>
              </div>
              <button
                type="button"
                onClick={() => setActiveCondition(null)}
                className="text-[10px] text-blue-600 hover:text-blue-800 font-bold ml-1 shrink-0"
              >
                Bỏ chọn
              </button>
            </div>
          )}

          {/* Conditions list badges */}
          <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
            {filteredConditions.map((c) => {
              const isActive = activeCondition === c.code;
              return (
                <button
                  key={c.code}
                  type="button"
                  onClick={() =>
                    setActiveCondition((prev) => (prev === c.code ? null : c.code))
                  }
                  className={`w-full flex items-center gap-2.5 p-2 rounded-lg text-left text-xs transition-all border ${
                    isActive
                      ? 'ring-2 ring-blue-500 bg-blue-50 border-blue-300 shadow-sm'
                      : 'border-gray-100 hover:bg-gray-50 hover:border-gray-200'
                  }`}
                >
                  {/* Badge: hiển thị badge text với bgColor nếu có, fallback sang code */}
                  <span
                    className="w-9 h-6 rounded flex items-center justify-center text-[10px] font-bold shrink-0 shadow-sm"
                    style={{
                      backgroundColor: c.bgColor || c.color,
                      color: '#ffffff',
                    }}
                  >
                    {c.badge || c.code}
                  </span>
                  <span
                    className={`truncate font-medium ${
                      isActive ? 'text-blue-900 font-semibold' : 'text-gray-700'
                    }`}
                  >
                    {c.label}
                  </span>
                </button>
              );
            })}
            {filteredConditions.length === 0 && (
              <p className="text-xs text-gray-400 text-center py-4 italic">
                Không tìm thấy bệnh lý
              </p>
            )}
          </div>
        </aside>
      )}

      {/* CENTER (flex-1) */}
      <main className="flex-1 flex flex-col p-6 overflow-y-auto bg-gray-50 print:p-2 print:w-full h-screen">
        {/* Top bar info */}
        <div className="flex items-center justify-between pb-4 mb-4 border-b border-gray-200">
          <div>
            <h1 className="text-lg font-bold text-gray-800">
              {customerId ? `Bệnh nhân: #${customerId}` : 'Sơ đồ răng EMR'}
            </h1>
            <p className="text-xs text-gray-500">
              {clonedFromId && (
                <span className="mr-3 text-blue-600 font-semibold cursor-pointer hover:underline" onClick={() => {
                  const chart = charts.find(c => c.id === clonedFromId);
                  if (chart) loadChartData(chart);
                }}>
                  Tiếp nối từ Sơ đồ {charts.find(c => c.id === clonedFromId)?.sequence_num}
                </span>
              )}
              {isReadOnly ? 'Chế độ xem sơ đồ (Chỉ đọc)' : 'Chọn bệnh lý bên trái và thao tác lên răng'}
            </p>
          </div>
          <div className="flex items-center gap-3">
            {activeCondition && !isReadOnly && (
              <div className="hidden sm:flex items-center gap-2 text-xs bg-amber-50 border border-amber-200 text-amber-800 px-3 py-1.5 rounded-lg">
                <span>Đang ở chế độ áp dụng bệnh lý:</span>
                <span className="font-bold underline">{activeCondition}</span>
              </div>
            )}
            
            {/* Lịch sử sơ đồ dropdown */}
            <select
              value={currentChartId || 'new'}
              onChange={(e) => {
                const val = e.target.value;
                if (val === 'new') {
                  handleCreateNew();
                } else if (val === 'continue') {
                  handleContinue();
                } else {
                  const chart = charts.find(c => c.id === Number(val));
                  if (chart) loadChartData(chart);
                }
              }}
              className="p-1.5 text-xs font-semibold border border-gray-300 rounded-lg bg-white shadow-sm focus:ring-2 focus:ring-blue-500"
            >
              <option value="" disabled>Lịch sử Sơ đồ...</option>
              {charts.map(c => (
                <option key={c.id} value={c.id}>
                  Sơ đồ {c.sequence_num} ({new Date(c.created_at).toLocaleDateString()}) - Xem
                </option>
              ))}
              <option value="new">Tạo sơ đồ mới</option>
              {currentChartId && isReadOnly && <option value="continue">Tiếp nối sơ đồ này</option>}
            </select>
          </div>
        </div>

        {/* TOOTH CHART */}
        <div className="bg-white rounded-xl border border-gray-200 p-4 shadow-sm mb-6">
          {/* HÀM TRÊN label */}
          <div className="text-center text-xs font-bold text-gray-500 tracking-wider mb-3 uppercase">
            HÀM TRÊN
          </div>

          {/* Upper Row: Q1 | Q2 */}
          <div className="overflow-x-auto pb-2">
            <div className="flex items-center justify-center min-w-max gap-1">
              {/* Q1: 18 down to 11 */}
              <div className="flex items-center gap-1">
                {Q1.map((num) => renderTooth(num))}
              </div>

              {/* Midline divider */}
              <div className="w-0.5 bg-gray-400 h-40 mx-4 self-center rounded-full" />

              {/* Q2: 21 up to 28 */}
              <div className="flex items-center gap-1">
                {Q2.map((num) => renderTooth(num))}
              </div>
            </div>
          </div>

          {/* Horizontal divider between Upper and Lower jaws */}
          <div className="border-t-2 border-dashed border-gray-300 my-4 w-full" />

          {/* Lower Row: Q3 | Q4 */}
          <div className="overflow-x-auto pb-2">
            <div className="flex items-center justify-center min-w-max gap-1">
              {/* Q3: 48 down to 41 */}
              <div className="flex items-center gap-1">
                {Q3.map((num) => renderTooth(num))}
              </div>

              {/* Midline divider */}
              <div className="w-0.5 bg-gray-400 h-28 mx-2 self-center rounded-full" />

              {/* Q4: 31 up to 38 */}
              <div className="flex items-center gap-1">
                {Q4.map((num) => renderTooth(num))}
              </div>
            </div>
          </div>

          {/* HÀM DƯỚI label */}
          <div className="text-center text-xs font-bold text-gray-500 tracking-wider mt-3 uppercase">
            HÀM DƯỚI
          </div>
        </div>

                {/* BẢNG TÓM TẮT BỆNH LÝ */}
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mb-6">
          <div className="px-4 py-3 border-b border-gray-200 bg-gray-50">
            <h3 className="text-sm font-bold text-gray-800 uppercase tracking-wide">
              Bảng Ghi nhận Tình trạng Răng
            </h3>
          </div>
          <div className="p-0">
            {conditionRows.length === 0 ? (
              <p className="text-xs text-gray-400 text-center py-6 italic">
                Chưa có bệnh lý nào được ghi nhận. Hãy chọn bệnh lý ở menu bên trái và click lên răng hoặc mặt răng.
              </p>
            ) : (
              <div className="overflow-x-auto max-h-60 overflow-y-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead className="sticky top-0 bg-gray-50 shadow-sm">
                    <tr className="border-b border-gray-200 text-gray-600">
                      <th className="p-3 font-bold w-24">Số răng</th>
                      <th className="p-3 font-bold w-48">Mặt răng</th>
                      <th className="p-3 font-bold w-32">Mã bệnh lý</th>
                      <th className="p-3 font-bold">Tên bệnh lý</th>
                      <th className="p-3 font-bold w-24">Phân loại</th>
                      <th className="p-3 font-bold">Điều trị</th>
                      <th className="p-3 font-bold">Ghi chú</th>
                      <th className="p-3 font-bold w-20 text-center">Xóa</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {conditionRows.map((row, idx) => {
                      const rowKey = `${row.toothNum}_${row.isWhole ? 'whole' : row.surfaceKey}`;
                      const notes = conditionNotes[rowKey] || { phanLoai: '', dieuTri: '', ghiChu: '' };
                      return (
                      <tr key={idx} className="hover:bg-gray-50 transition-colors">
                        <td className="p-3 font-bold text-gray-800 text-base">
                          R{row.toothNum}
                        </td>
                        <td className="p-3 text-gray-600 font-medium">{row.surface}</td>
                        <td className="p-3">
                          <span
                            className="px-3 py-1 rounded text-xs font-bold shadow-sm"
                            style={{
                              backgroundColor: row.color,
                              color: row.code === 'NL' ? '#065f46' : '#ffffff',
                            }}
                          >
                            {row.code}
                          </span>
                        </td>
                        <td className="p-3 font-bold text-gray-800 text-sm">
                          {row.label}
                        </td>
                        <td className="p-3">
                          <select
                            className="w-full p-1.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white"
                            value={notes.phanLoai}
                            onChange={(e) => setConditionNotes(prev => ({ ...prev, [rowKey]: { ...notes, phanLoai: e.target.value } }))}
                            disabled={isReadOnly}
                          >
                            <option value=""></option>
                            <option value="P">P</option>
                            <option value="N">N</option>
                          </select>
                        </td>
                        <td className="p-3">
                          <input
                            type="text"
                            className="w-full p-1.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white read-only:bg-gray-100"
                            value={notes.dieuTri}
                            onChange={(e) => setConditionNotes(prev => ({ ...prev, [rowKey]: { ...notes, dieuTri: e.target.value } }))}
                            readOnly={isReadOnly}
                          />
                        </td>
                        <td className="p-3">
                          <input
                            type="text"
                            className="w-full p-1.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white read-only:bg-gray-100"
                            value={notes.ghiChu}
                            onChange={(e) => setConditionNotes(prev => ({ ...prev, [rowKey]: { ...notes, ghiChu: e.target.value } }))}
                            readOnly={isReadOnly}
                          />
                        </td>
                        <td className="p-3 text-center">
                          {!isReadOnly && (
                            <button
                              type="button"
                              onClick={() => handleRemoveCondition(row)}
                              className="text-red-500 hover:text-red-700 font-bold px-3 py-1.5 rounded border border-red-200 hover:bg-red-50 transition-colors"
                            >
                              Xóa
                            </button>
                          )}
                        </td>
                      </tr>
                    )})}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
        {/* TEXTAREA SECTION (2x2 grid) */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1 uppercase tracking-wide">
              Ghi chú
            </label>
            <textarea
              value={ghiChu}
              onChange={(e) => setGhiChu(e.target.value)}
              rows={3}
              readOnly={isReadOnly}
              placeholder="Nhập ghi chú tổng quát..."
              className="w-full p-2.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 read-only:bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1 uppercase tracking-wide">
              Cận lâm sàng
            </label>
            <textarea
              value={canLamSang}
              onChange={(e) => setCanLamSang(e.target.value)}
              rows={3}
              readOnly={isReadOnly}
              placeholder="Nhập kết quả cận lâm sàng (X-Quang, xét nghiệm...)..."
              className="w-full p-2.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 read-only:bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1 uppercase tracking-wide">
              Chẩn đoán
            </label>
            <textarea
              value={chanDoan}
              onChange={(e) => setChanDoan(e.target.value)}
              rows={3}
              readOnly={isReadOnly}
              placeholder="Nhập chẩn đoán bệnh..."
              className="w-full p-2.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 read-only:bg-gray-100"
            />
          </div>
          <div>
            <label className="block text-xs font-bold text-gray-700 mb-1 uppercase tracking-wide">
              Chỉ định điều trị
            </label>
            <textarea
              value={chiDinhDieuTri}
              onChange={(e) => setChiDinhDieuTri(e.target.value)}
              rows={3}
              readOnly={isReadOnly}
              placeholder="Nhập chỉ định phác đồ điều trị..."
              className="w-full p-2.5 text-xs border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 read-only:bg-gray-100"
            />
          </div>
        </div>

        {/* ACTION BUTTONS: Luu, In & Dong */}
        <div className="flex justify-end gap-3 pt-4 border-t border-gray-200 print:hidden items-center">
          {saveMsg && (
            <span className={`text-xs font-bold px-3 py-1 rounded-full ${saveMsg === 'Đã lưu!' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'}`}>
              {saveMsg}
            </span>
          )}
          {isReadOnly ? (
            <button
              type="button"
              onClick={handleContinue}
              className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors flex items-center gap-1.5"
            >
              Tạo tiếp nối
            </button>
          ) : (
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaving}
              className="px-6 py-2.5 bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-sm transition-colors flex items-center gap-1.5"
            >
              {isSaving ? 'Đang lưu...' : 'Lưu Bệnh Án'}
            </button>
          )}
          <button
            type="button"
            onClick={() => {
              if (typeof window !== 'undefined') {
                window.print();
              }
            }}
            className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold rounded-lg shadow-sm transition-colors flex items-center gap-1.5"
          >
            In
          </button>
          <button
            type="button"
            onClick={handleReset}
            className="px-6 py-2.5 bg-gray-200 hover:bg-gray-300 text-gray-700 text-xs font-bold rounded-lg transition-colors"
          >
            Đóng
          </button>
        </div>
      </main>
    </div>
  );
}
