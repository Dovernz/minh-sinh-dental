from datetime import datetime, timedelta, time
from types import SimpleNamespace
from django.utils import timezone
from .models import Clinic, Booking, TimeSlot

ACTIVE_BOOKING_STATUSES = ['Pending', 'Confirmed', 'In_progress', 'booked', 'Booked', 'paid', 'Paid', 'Khám', 'Upcoming']
INACTIVE_BOOKING_STATUSES = ['Completed', 'completed', 'Cancelled', 'cancelled', 'Canceled', 'canceled', 'Đã xong', 'Đã hủy']

def get_clinic_total_chairs(clinic):
    return clinic.total_chairs if (clinic and clinic.total_chairs and clinic.total_chairs > 0) else 5

def make_aware_dt(target_date, target_time):
    dt = datetime.combine(target_date, target_time)
    if timezone.is_naive(dt):
        return timezone.make_aware(dt, timezone.get_current_timezone())
    return dt

def get_slot_capacity(clinic, target_date, start_time_obj, duration_minutes=30, requested_count=1, extra_occupied_spans=None):
    start_dt = make_aware_dt(target_date, start_time_obj)
    end_dt = start_dt + timedelta(minutes=duration_minutes)
    
    db_occupied = Booking.objects.filter(
        clinic=clinic,
        start_time__lt=end_dt,
        end_time__gt=start_dt
    ).exclude(status__in=INACTIVE_BOOKING_STATUSES).count()
    
    batch_overlap = 0
    if extra_occupied_spans:
        for span in extra_occupied_spans:
            if span['start'] < end_dt and span['end'] > start_dt:
                batch_overlap += 1
                
    active_bookings = db_occupied + batch_overlap
    total_chairs = get_clinic_total_chairs(clinic)
    available_chairs = max(0, total_chairs - active_bookings)
    is_full = available_chairs <= 0
    is_available = available_chairs >= requested_count
    
    warning_message = None if is_available else f"Cảnh báo: Khung giờ {start_time_obj.strftime('%H:%M')} tại {clinic.name} chỉ còn {available_chairs}/{total_chairs} ghế trống, không đủ cho {requested_count} khách!"
    
    return {
        'total_chairs': total_chairs,
        'active_bookings': active_bookings,
        'occupied_chairs': active_bookings,
        'available_chairs': available_chairs,
        'is_full': is_full,
        'is_available': is_available,
        'requested_passengers': requested_count,
        'warning_message': warning_message,
        'warning': warning_message
    }

def get_valid_time_slots_from(start_time_obj):
    db_slots = list(TimeSlot.objects.all().order_by('start_time'))
    
    if not db_slots:
        slots = []
        current = time(8, 0)
        end_limit = time(19, 0)
        while current <= end_limit:
            dt_dummy = datetime.combine(datetime.today(), current) + timedelta(minutes=30)
            next_time = dt_dummy.time()
            slots.append(SimpleNamespace(start_time=current, end_time=next_time))
            current = next_time
        db_slots = slots
        
    filtered_slots = [s for s in db_slots if s.start_time >= start_time_obj]
    
    if (not filtered_slots or filtered_slots[0].start_time != start_time_obj) and start_time_obj < time(23, 30):
        dt_dummy = datetime.combine(datetime.today(), start_time_obj) + timedelta(minutes=30)
        end_time_obj = dt_dummy.time()
        prepend_slot = SimpleNamespace(start_time=start_time_obj, end_time=end_time_obj)
        filtered_slots.insert(0, prepend_slot)
        
    return filtered_slots

def compute_auto_distribution(clinic, target_date, requested_start_time, patients_list, default_duration=30):
    candidate_slots = get_valid_time_slots_from(requested_start_time)
    extra_occupied_spans = []
    remaining = list(enumerate(patients_list))
    initial_slot_available = None
    distributed_patients = []
    distribution_summary = []
    
    for slot in candidate_slots:
        if not remaining:
            break
            
        cap = get_slot_capacity(
            clinic, 
            target_date, 
            slot.start_time, 
            duration_minutes=default_duration, 
            requested_count=len(remaining), 
            extra_occupied_spans=extra_occupied_spans
        )
        
        if initial_slot_available is None:
            initial_slot_available = cap['available_chairs']
            
        avail = cap['available_chairs']
        if avail <= 0:
            continue
            
        take = remaining[:avail]
        remaining = remaining[avail:]
        
        for idx, p in take:
            p_dur = int(p.get('duration') or default_duration)
            p_start_dt = make_aware_dt(target_date, slot.start_time)
            p_end_dt = p_start_dt + timedelta(minutes=p_dur)
            extra_occupied_spans.append({'start': p_start_dt, 'end': p_end_dt})
            
            entry = dict(p)
            entry['patient_index'] = idx
            entry['original_start_time'] = requested_start_time.strftime('%H:%M')
            entry['assigned_start_time'] = slot.start_time.strftime('%H:%M')
            entry['assigned_end_time'] = timezone.localtime(p_end_dt).strftime('%H:%M')
            entry['assigned_start_dt'] = p_start_dt
            entry['assigned_end_dt'] = p_end_dt
            entry['duration'] = p_dur
            entry['is_shifted'] = (slot.start_time != requested_start_time)
            distributed_patients.append(entry)
            
        distribution_summary.append({
            'start_time': slot.start_time.strftime('%H:%M'),
            'end_time': slot.end_time.strftime('%H:%M') if hasattr(slot, 'end_time') and slot.end_time else (datetime.combine(target_date, slot.start_time) + timedelta(minutes=default_duration)).time().strftime('%H:%M'),
            'assigned_count': len(take),
            'available_before': avail,
            'available_after': max(0, avail - len(take))
        })
        
    if initial_slot_available is None:
        initial_slot_available = 0
        
    distributed_patients.sort(key=lambda x: x['patient_index'])
    
    needs_distribution = any(p['is_shifted'] for p in distributed_patients) or (len(remaining) > 0)
    can_fulfill_all = (len(remaining) == 0)
    unassigned_count = len(remaining)
    
    warning_message = None
    if not can_fulfill_all:
        warning_message = f"Khung giờ {requested_start_time.strftime('%H:%M')} và các khung giờ còn lại trong ngày không đủ ghế cho {unassigned_count} khách."
    elif needs_distribution:
        shifted_count = sum(1 for p in distributed_patients if p['is_shifted'])
        total_chairs = get_clinic_total_chairs(clinic)
        warning_message = f"Khung giờ {requested_start_time.strftime('%H:%M')} chỉ còn {initial_slot_available}/{total_chairs} ghế trống. {shifted_count} khách vượt ngưỡng đã được phân phối sang khung giờ tiếp theo."
        
    return {
        'clinic_id': clinic.clinic_id,
        'clinic_name': clinic.name,
        'date': target_date.strftime('%Y-%m-%d'),
        'requested_start_time': requested_start_time.strftime('%H:%M'),
        'total_chairs': get_clinic_total_chairs(clinic),
        'requested_count': len(patients_list),
        'initial_slot_available': initial_slot_available,
        'needs_distribution': needs_distribution,
        'can_fulfill_all': can_fulfill_all,
        'unassigned_count': unassigned_count,
        'warning_message': warning_message,
        'distribution_summary': distribution_summary,
        'distributed_patients': distributed_patients
    }