from django import template
from django.utils import timezone
from django.db.models import Sum

register = template.Library()

@register.simple_tag
def get_dashboard_stats():
    today = timezone.now().date()
    stats = {'revenue': '0', 'bookings': '0', 'customers': '0'}
    try:
        from booking.models import Billing
        rev = Billing.objects.filter(created_at__date=today).aggregate(Sum('final_total'))['final_total__sum']
        if rev: stats['revenue'] = "{:,.0f}".format(rev)
    except Exception: pass
    
    try:
        from booking.models import Booking
        stats['bookings'] = str(Booking.objects.filter(created_at__date=today).count())
    except Exception: pass
    
    try:
        from booking.models import Customer
        stats['customers'] = str(Customer.objects.filter(created_at__date=today).count())
    except Exception: pass
    
    return stats


@register.simple_tag
def get_dashboard_charts():
    from datetime import timedelta
    from django.utils import timezone
    today = timezone.now().date()
    next_7 = today + timedelta(days=7)
    data = {'clinics': [], 'clinic_totals': [], 'slots': [], 'has_data': False}
    try:
        from booking.models import Booking
        # Tự động dò tên trường lưu ngày đặt lịch của bạn
        opts = [f.name for f in Booking._meta.get_fields()]
        date_field = 'booking_date'
        if 'date' in opts: date_field = 'date'
        elif 'appointment_date' in opts: date_field = 'appointment_date'
        elif 'schedule_date' in opts: date_field = 'schedule_date'

        # Lọc các booking trong 7 ngày tới
        bookings = Booking.objects.filter(**{f"{date_field}__range": [today, next_7]})
        
        clinics_set = set()
        slots_dict = {}
        
        # Bóc tách dữ liệu theo Cơ sở và Khung giờ
        for b in bookings:
            c_name = getattr(b.clinic, 'name', str(b.clinic)) if hasattr(b, 'clinic') and b.clinic else 'Chưa phân bổ'
            
            t_obj = getattr(b, 'time_slot', None) or getattr(b, 'timeslot', None)
            if t_obj:
                t_name = getattr(t_obj, 'name', getattr(t_obj, 'time', str(t_obj)))
            else:
                t_name = 'Không rõ'
            t_name = str(t_name)
            
            clinics_set.add(c_name)
            if t_name not in slots_dict:
                slots_dict[t_name] = {}
            slots_dict[t_name][c_name] = slots_dict[t_name].get(c_name, 0) + 1
            
        clinic_list = sorted(list(clinics_set))
        data['clinics'] = clinic_list
        
        # Sắp xếp thành dòng (Rows) cho giao diện Table
        for t_name, c_data in slots_dict.items():
            row = {'time': t_name, 'counts': []}
            for c in clinic_list:
                row['counts'].append(c_data.get(c, 0))
            row['total'] = sum(c_data.values())
            data['slots'].append(row)
            
        data['slots'] = sorted(data['slots'], key=lambda x: x['time'])
        
        # Tính tổng theo Cơ sở
        for c in clinic_list:
            total = sum(slots_dict[s].get(c, 0) for s in slots_dict)
            data['clinic_totals'].append({'name': c, 'count': total})
            
        if data['slots']:
            data['has_data'] = True
            
    except Exception as e:
        pass
        
    return data
