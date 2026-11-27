'use client';

import React from 'react';
import {
  AlertTriangle,
  CheckCircle2,
  Clock,
  Info,
  Loader2,
  Sparkles,
  Users,
  Zap,
  ShieldAlert
} from 'lucide-react';
import {
  CapacityCheckResponse,
  DistributePreviewResponse,
  normalizeDistributionSummary
} from '@/lib/bookingCapacityApi';

export interface CapacityDistributionPanelProps {
  selectedTime: string;
  totalGroupSize: number;
  capacityCheck: CapacityCheckResponse | null;
  capacityLoading?: boolean;
  distributePreview: DistributePreviewResponse | null;
  distributeLoading?: boolean;
  autoDistribute: boolean;
  onAutoDistributeChange: (val: boolean) => void;
  compact?: boolean;
}

export default function CapacityDistributionPanel({
  selectedTime,
  totalGroupSize,
  capacityCheck,
  capacityLoading = false,
  distributePreview,
  distributeLoading = false,
  autoDistribute,
  onAutoDistributeChange,
  compact = false
}: CapacityDistributionPanelProps) {
  // Compute real free chairs logic
  const realFreeChairs = capacityCheck
    ? Math.max(0, capacityCheck.total_chairs - capacityCheck.active_bookings)
    : null;
  const availableChairs = capacityCheck?.available_chairs ?? realFreeChairs ?? 0;

  // 1. Logic cảnh báo rõ ràng khi số khách > 5 HOẶC > số ghế còn lại (availableChairs) HOẶC is_full / !is_available
  const isOverGroupLimit = totalGroupSize > 5;
  const isFullOrExceeded = capacityCheck
    ? capacityCheck.is_full || !capacityCheck.is_available || totalGroupSize > availableChairs || isOverGroupLimit
    : isOverGroupLimit;

  const isExactFit = capacityCheck
    ? !capacityCheck.is_full && totalGroupSize === availableChairs && availableChairs > 0
    : false;

  // 2. Trong showDistributeSection: hiển thị khi !compact && (...)
  const showDistributeSection =
    !compact &&
    (distributeLoading ||
      (distributePreview &&
        (distributePreview.needs_distribution || totalGroupSize > availableChairs)) ||
      totalGroupSize > 5 ||
      (capacityCheck ? totalGroupSize > availableChairs : false));

  const normalizedItems = distributePreview
    ? normalizeDistributionSummary(
        distributePreview.distribution_summary,
        distributePreview.distributed_patients
      )
    : [];

  return (
    <div className="w-full min-w-0 space-y-3 font-sans">
      {/* Real-time Capacity Loading State */}
      {capacityLoading && !capacityCheck && (
        <div className="w-full min-w-0 rounded-xl border border-blue-100 bg-blue-50/70 p-3.5 text-blue-800 shadow-sm transition-all dark:border-blue-900/40 dark:bg-blue-950/30 dark:text-blue-200">
          <div className="flex items-center gap-2.5 text-xs font-medium sm:text-sm">
            <Loader2 className="h-4 w-4 shrink-0 animate-spin text-blue-600 dark:text-blue-400" />
            <span className="truncate">Đang kiểm tra số ghế trống theo thời gian thực...</span>
          </div>
        </div>
      )}

      {/* Main Capacity Status Card */}
      {(capacityCheck || totalGroupSize > 5) && (
        <div
          className={`w-full min-w-0 rounded-xl border p-3.5 shadow-sm transition-all sm:p-4 ${
            isFullOrExceeded
              ? 'border-red-200 bg-red-50/60 dark:border-red-900/40 dark:bg-red-950/20'
              : isExactFit
              ? 'border-amber-200 bg-amber-50/60 dark:border-amber-900/40 dark:bg-amber-950/20'
              : 'border-emerald-200 bg-emerald-50/50 dark:border-emerald-900/40 dark:bg-emerald-950/20'
          }`}
        >
          {/* Header Info */}
          <div className="flex flex-wrap items-center justify-between gap-2 border-b border-slate-200/60 pb-3 dark:border-slate-800/60">
            <div className="flex items-center gap-2 min-w-0">
              <Clock className="h-4 w-4 shrink-0 text-slate-500 dark:text-slate-400" />
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-300 sm:text-sm">
                Khung giờ {selectedTime}
              </span>
            </div>

            <div className="flex items-center gap-1.5 flex-wrap">
              <span
                className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                  isFullOrExceeded
                    ? 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300'
                    : isExactFit
                    ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-300'
                    : 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/50 dark:text-emerald-300'
                }`}
              >
                {isFullOrExceeded ? (
                  <ShieldAlert className="h-3.5 w-3.5 shrink-0" />
                ) : isExactFit ? (
                  <AlertTriangle className="h-3.5 w-3.5 shrink-0" />
                ) : (
                  <CheckCircle2 className="h-3.5 w-3.5 shrink-0" />
                )}
                {isFullOrExceeded
                  ? 'Thiếu ghế'
                  : isExactFit
                  ? 'Vừa đủ ghế'
                  : 'Sẵn sàng'}
              </span>
            </div>
          </div>

          {/* Metrics summary */}
          {capacityCheck && (
            <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-3 text-xs sm:text-sm">
              <div className="rounded-lg bg-white/70 p-2 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800">
                <span className="block text-slate-500 dark:text-slate-400 text-xs">Tổng ghế</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">
                  {capacityCheck.total_chairs} ghế
                </span>
              </div>
              <div className="rounded-lg bg-white/70 p-2 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800">
                <span className="block text-slate-500 dark:text-slate-400 text-xs">Đã đặt trước</span>
                <span className="font-semibold text-slate-800 dark:text-slate-200">
                  {capacityCheck.active_bookings} ghế
                </span>
              </div>
              <div className="col-span-2 sm:col-span-1 rounded-lg bg-white/70 p-2 dark:bg-slate-900/50 border border-slate-100 dark:border-slate-800">
                <span className="block text-slate-500 dark:text-slate-400 text-xs">Còn trống</span>
                <span
                  className={`font-semibold ${
                    isFullOrExceeded
                      ? 'text-red-600 dark:text-red-400'
                      : 'text-emerald-600 dark:text-emerald-400'
                  }`}
                >
                  {availableChairs} / {capacityCheck.total_chairs} ghế
                </span>
              </div>
            </div>
          )}

          {/* Warning Message if Full / Exceeded / > 5 */}
          {isFullOrExceeded && (
            <div className="mt-3 flex gap-2.5 rounded-lg border border-red-200 bg-red-100/70 p-3 text-xs text-red-900 dark:border-red-800/40 dark:bg-red-950/40 dark:text-red-200 sm:text-sm">
              <AlertTriangle className="h-4 w-4 shrink-0 text-red-600 dark:text-red-400 mt-0.5" />
              <div className="min-w-0 flex-1 break-words">
                <span className="font-bold block uppercase tracking-wide text-[11px] text-red-700 dark:text-red-300">
                  Cảnh báo giới hạn ghế trống
                </span>
                <p className="mt-0.5">
                  {isOverGroupLimit && !capacityCheck
                    ? `Nhóm có ${totalGroupSize} khách (vượt ngưỡng tối đa 5 ghế/khung giờ). Hệ thống sẽ tự động phân bổ các khách vượt ngưỡng sang khung giờ trống tiếp theo nếu bật Tự động phân phối.`
                    : capacityCheck?.warning_message ||
                      capacityCheck?.warning ||
                      (isOverGroupLimit
                        ? `Nhóm có ${totalGroupSize} khách (vượt ngưỡng tối đa 5 ghế/khung giờ). Hệ thống sẽ tự động phân bổ các khách vượt ngưỡng sang khung giờ trống tiếp theo nếu bật Tự động phân phối.`
                        : `Khung giờ ${selectedTime} chỉ còn ${availableChairs} ghế trống, trong khi nhóm có ${totalGroupSize} khách.`)}
                </p>
              </div>
            </div>
          )}

          {/* Exact Fit Warning */}
          {isExactFit && !isOverGroupLimit && (
            <div className="mt-3 flex gap-2.5 rounded-lg border border-amber-200 bg-amber-100/70 p-2.5 text-xs text-amber-900 dark:border-amber-800/40 dark:bg-amber-950/40 dark:text-amber-200 sm:text-sm">
              <Info className="h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
              <div className="min-w-0 flex-1 break-words">
                <span className="font-semibold">Khung giờ vừa chạm giới hạn ghế trống: </span>
                <span>Số khách đặt vừa đúng bằng số ghế còn trống ({availableChairs} ghế).</span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Auto-Distribution Preview Section */}
      {showDistributeSection && (
        <div className="w-full min-w-0 rounded-xl border border-indigo-200 bg-gradient-to-br from-indigo-50/70 to-slate-50/70 p-3.5 shadow-sm dark:border-indigo-900/50 dark:from-indigo-950/30 dark:to-slate-900/30 sm:p-4">
          <div className="flex items-center gap-2 border-b border-indigo-100 pb-2.5 dark:border-indigo-900/40">
            <Zap className="h-4.5 w-4.5 shrink-0 text-indigo-600 dark:text-indigo-400" />
            <h4 className="text-xs font-bold uppercase tracking-wider text-indigo-950 dark:text-indigo-200 sm:text-sm break-words">
              Kế hoạch tự động phân phối sang khung giờ trống tiếp theo
            </h4>
          </div>

          <div className="mt-3 space-y-3">
            {distributeLoading ? (
              <div className="flex items-center justify-center gap-2 py-4 text-xs font-medium text-indigo-700 dark:text-indigo-300 sm:text-sm">
                <Loader2 className="h-4 w-4 animate-spin text-indigo-600 dark:text-indigo-400" />
                <span>Đang tính toán phương án chia ca...</span>
              </div>
            ) : distributePreview ? (
              <>
                {distributePreview.warning_message && (
                  <p className="text-xs text-indigo-900 dark:text-indigo-200 break-words bg-indigo-100/60 dark:bg-indigo-900/30 p-2.5 rounded-lg border border-indigo-200/50 dark:border-indigo-800/50">
                    {distributePreview.warning_message}
                  </p>
                )}

                {/* Distributed slots grid */}
                {normalizedItems.length > 0 && (
                  <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
                    {normalizedItems.map((item, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between gap-2 rounded-lg border border-indigo-200/70 bg-white/90 p-2.5 text-xs dark:border-indigo-800/60 dark:bg-slate-900/80 shadow-xs"
                      >
                        <div className="flex items-center gap-1.5 min-w-0">
                          <Clock className="h-3.5 w-3.5 shrink-0 text-indigo-500 dark:text-indigo-400" />
                          <span className="font-semibold text-slate-800 dark:text-slate-200 truncate">
                            {item.time}
                          </span>
                        </div>
                        <span className="inline-flex items-center gap-1 shrink-0 rounded-full bg-indigo-100 px-2 py-0.5 text-[11px] font-bold text-indigo-700 dark:bg-indigo-900/50 dark:text-indigo-300">
                          <Users className="h-3 w-3" />
                          {item.count} khách
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {/* Unassigned Warning */}
                {(!distributePreview.can_fulfill_all ||
                  (distributePreview.unassigned_count ?? 0) > 0) && (
                  <div className="flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 p-2.5 text-xs text-red-800 dark:border-red-900/40 dark:bg-red-950/30 dark:text-red-300">
                    <AlertTriangle className="h-4 w-4 shrink-0 text-red-600 dark:text-red-400 mt-0.5" />
                    <span className="break-words">
                      Chú ý: Có{' '}
                      <strong className="font-semibold">
                        {distributePreview.unassigned_count} khách
                      </strong>{' '}
                      chưa thể xếp vào các khung giờ còn lại trong ngày do phòng khám đã hết ghế.
                    </span>
                  </div>
                )}

                {/* Toggle Checkbox */}
                <div className="mt-3 pt-3 border-t border-indigo-100 dark:border-indigo-900/40">
                  <label className="flex items-start gap-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={autoDistribute}
                      onChange={(e) => onAutoDistributeChange(e.target.checked)}
                      className="mt-0.5 h-4 w-4 rounded border-indigo-300 text-indigo-600 focus:ring-indigo-500 dark:border-indigo-700 dark:bg-slate-900"
                    />
                    <div className="min-w-0 flex-1">
                      <span className="text-xs font-semibold text-indigo-950 dark:text-indigo-200 group-hover:text-indigo-600 transition-colors sm:text-sm break-words block">
                        Tự động phân phối lịch sang khung giờ sau (auto_distribute)
                      </span>
                      <p className="mt-0.5 text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 break-words leading-relaxed">
                        {autoDistribute
                          ? 'Hệ thống sẽ tự động xếp những khách vượt quá số ghế vào các khung giờ trống liền kề khi đặt lịch.'
                          : 'Chỉ đặt tại khung giờ đã chọn; nếu vượt quá ghế trống, đơn có thể bị từ chối hoặc cần chỉnh giờ thủ công.'}
                      </p>
                    </div>
                  </label>
                </div>
              </>
            ) : (
              /* Fallback when distributePreview is null but totalGroupSize > 5 || capacityCheck capacity exceeded */
              <>
                <p className="text-xs text-indigo-900 dark:text-indigo-200 break-words bg-indigo-100/60 dark:bg-indigo-900/30 p-2.5 rounded-lg border border-indigo-200/50 dark:border-indigo-800/50">
                  Nhóm của bạn có {totalGroupSize} khách, vượt quá giới hạn hoặc số ghế trống hiện tại. Kích hoạt tính năng tự động phân phối để hệ thống sắp xếp sang các khung giờ trống tiếp theo.
                </p>

                {/* Toggle Checkbox */}
                <div className="mt-3 pt-3 border-t border-indigo-100 dark:border-indigo-900/40">
                  <label className="flex items-start gap-3 cursor-pointer group">
                    <input
                      type="checkbox"
                      checked={autoDistribute}
                      onChange={(e) => onAutoDistributeChange(e.target.checked)}
                      className="mt-0.5 h-4 w-4 rounded border-indigo-300 text-indigo-600 focus:ring-indigo-500 dark:border-indigo-700 dark:bg-slate-900"
                    />
                    <div className="min-w-0 flex-1">
                      <span className="text-xs font-semibold text-indigo-950 dark:text-indigo-200 group-hover:text-indigo-600 transition-colors sm:text-sm break-words block">
                        Tự động phân phối lịch sang khung giờ sau (auto_distribute)
                      </span>
                      <p className="mt-0.5 text-[11px] sm:text-xs text-slate-500 dark:text-slate-400 break-words leading-relaxed">
                        {autoDistribute
                          ? 'Hệ thống sẽ tự động xếp những khách vượt quá số ghế vào các khung giờ trống liền kề khi đặt lịch.'
                          : 'Chỉ đặt tại khung giờ đã chọn; nếu vượt quá ghế trống, đơn có thể bị từ chối hoặc cần chỉnh giờ thủ công.'}
                      </p>
                    </div>
                  </label>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

/**
 * Named Component: BookingDistributionSummaryBanner
 * Renders on Step 4 (E-Boarding Pass confirmation screen) when autoDistributed is true
 * or distributionSummary has items.
 */
export function BookingDistributionSummaryBanner({
  autoDistributed = false,
  warningMessage,
  distributionSummary,
  members
}: {
  autoDistributed?: boolean;
  warningMessage?: string | null;
  distributionSummary?: any;
  members?: Array<{ start_time: string; full_name: string }>;
}) {
  const normalized = normalizeDistributionSummary(distributionSummary, members);

  if (!autoDistributed && normalized.length <= 1 && !warningMessage) {
    return null;
  }

  return (
    <div className="w-full min-w-0 rounded-2xl border border-emerald-200 bg-gradient-to-br from-emerald-50/90 via-teal-50/50 to-white p-4 shadow-sm dark:border-emerald-900/40 dark:from-emerald-950/40 dark:via-slate-900 dark:to-slate-900 sm:p-5">
      <div className="flex items-center gap-2.5 border-b border-emerald-200/60 pb-3 dark:border-emerald-800/40">
        <div className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-emerald-100 text-emerald-700 dark:bg-emerald-900/60 dark:text-emerald-300">
          <Sparkles className="h-4 w-4" />
        </div>
        <div>
          <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-900 dark:text-emerald-200 sm:text-sm">
            Xác nhận Phân Phối Giờ Khám Tự Động
          </h4>
          <p className="text-[11px] text-emerald-700 dark:text-emerald-400 sm:text-xs">
            Lịch khám của nhóm đã được sắp xếp tối ưu theo năng lực phục vụ thực tế
          </p>
        </div>
      </div>

      {warningMessage && (
        <div className="mt-3 flex items-start gap-2 rounded-lg bg-amber-100/80 p-2.5 text-xs text-amber-900 dark:bg-amber-950/40 dark:text-amber-200 border border-amber-200/50">
          <Info className="h-4 w-4 shrink-0 text-amber-600 dark:text-amber-400 mt-0.5" />
          <span className="break-words">{warningMessage}</span>
        </div>
      )}

      {normalized.length > 0 && (
        <div className="mt-3.5 space-y-2">
          <span className="text-xs font-semibold text-slate-600 dark:text-slate-400 block">
            Chi tiết phân bổ các khung giờ:
          </span>
          <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {normalized.map((item, index) => (
              <div
                key={index}
                className="flex items-center justify-between gap-2 rounded-xl border border-emerald-200/70 bg-white/80 p-3 text-xs shadow-xs dark:border-emerald-800/50 dark:bg-slate-900/80"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <Clock className="h-4 w-4 shrink-0 text-emerald-600 dark:text-emerald-400" />
                  <span className="font-bold text-slate-800 dark:text-slate-100 truncate">
                    {item.time}
                  </span>
                </div>
                <span className="inline-flex items-center gap-1 shrink-0 rounded-full bg-emerald-100 px-2.5 py-0.5 text-xs font-bold text-emerald-800 dark:bg-emerald-900/60 dark:text-emerald-200">
                  <Users className="h-3 w-3" />
                  {item.count} khách
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
