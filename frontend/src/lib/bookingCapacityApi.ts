export interface CapacityCheckResponse {
  clinic_id: number;
  clinic_name?: string;
  date: string;
  start_time: string;
  total_chairs: number;
  active_bookings: number;
  occupied_chairs?: number;
  available_chairs: number;
  requested_passengers: number;
  is_full: boolean;
  is_available: boolean;
  warning_message?: string | null;
  warning?: string | null;
}

export interface DistributionSummarySlot {
  time?: string;
  start_time?: string;
  end_time?: string;
  count?: number;
  assigned_count?: number;
  available_chairs?: number;
}

export interface DistributedPatient {
  fullName?: string;
  full_name?: string;
  phone?: string;
  start_time: string;
  category_id?: number;
  service_name?: string;
  status?: string;
}

export interface DistributePreviewResponse {
  clinic_id: number;
  clinic_name?: string;
  date: string;
  requested_start_time: string;
  total_chairs: number;
  requested_count: number;
  initial_slot_available: number;
  needs_distribution: boolean;
  can_fulfill_all: boolean;
  unassigned_count: number;
  warning_message?: string | null;
  distribution_summary?: Array<DistributionSummarySlot | string> | Record<string, number> | null;
  distributed_patients?: DistributedPatient[];
}

export interface BookingCreateResponse {
  pnr_code?: string;
  group_code?: string;
  created_booking_ids?: number[];
  booking_id?: number;
  status?: string;
  auto_distributed?: boolean;
  warning_message?: string | null;
  distribution_summary?: Array<DistributionSummarySlot | string> | Record<string, number> | null;
  bookings?: Array<{
    id?: number;
    booking_id?: number;
    full_name?: string;
    fullName?: string;
    phone?: string;
    start_time?: string;
    service_name?: string;
  }>;
  message?: string;
  error?: string;
  warning?: string;
}

export async function fetchCapacityCheck(params: {
  clinicId: string | number;
  date: string;
  startTime: string;
  passengerCount: number;
  duration?: number;
  signal?: AbortSignal;
}): Promise<CapacityCheckResponse | null> {
  try {
    const duration = params.duration ?? 30;
    const url = `/api/capacity-check/?clinic_id=${encodeURIComponent(params.clinicId)}&date=${encodeURIComponent(params.date)}&start_time=${encodeURIComponent(params.startTime)}&passenger_count=${encodeURIComponent(params.passengerCount)}&duration=${encodeURIComponent(duration)}`;

    const response = await fetch(url, {
      method: 'GET',
      signal: params.signal,
    });

    if (!response.ok) {
      return null;
    }

    const data: CapacityCheckResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return null;
    }
    return null;
  }
}

export async function fetchDistributePreview(params: {
  clinicId: string | number;
  date: string;
  startTime: string;
  patients?: Array<{ fullName?: string; phone?: string; start_time?: string; category_id?: number }>;
  passengerCount?: number;
  duration?: number;
  signal?: AbortSignal;
}): Promise<DistributePreviewResponse | null> {
  try {
    const body = {
      clinic_id: Number(params.clinicId),
      date: params.date,
      start_time: params.startTime,
      patients: params.patients,
      passenger_count: params.passengerCount,
      duration: params.duration ?? 30,
    };

    const response = await fetch('/api/bookings/distribute-preview/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      signal: params.signal,
    });

    if (!response.ok) {
      return null;
    }

    const data: DistributePreviewResponse = await response.json();
    return data;
  } catch (error) {
    if (error instanceof Error && error.name === 'AbortError') {
      return null;
    }
    return null;
  }
}

export function normalizeDistributionSummary(
  summary?: Array<DistributionSummarySlot | string> | Record<string, number> | null,
  distributedPatients?: DistributedPatient[]
): Array<{ time: string; count: number }> {
  const result: Array<{ time: string; count: number }> = [];

  if (summary) {
    if (Array.isArray(summary)) {
      for (const item of summary) {
        if (typeof item === 'string') {
          result.push({ time: item, count: 1 });
        } else if (item && typeof item === 'object') {
          const time = item.time || item.start_time || '';
          const count = item.count ?? item.assigned_count ?? item.available_chairs ?? 1;
          if (time) {
            result.push({ time, count });
          }
        }
      }
    } else if (typeof summary === 'object') {
      for (const [key, value] of Object.entries(summary)) {
        if (typeof value === 'number') {
          result.push({ time: key, count: value });
        }
      }
    }
  }

  // Fallback or supplementary population from distributedPatients if summary was empty
  if (result.length === 0 && distributedPatients && Array.isArray(distributedPatients)) {
    const countsMap = new Map<string, number>();
    for (const patient of distributedPatients) {
      if (patient.start_time) {
        const current = countsMap.get(patient.start_time) || 0;
        countsMap.set(patient.start_time, current + 1);
      }
    }
    for (const [time, count] of countsMap.entries()) {
      result.push({ time, count });
    }
  }

  return result;
}