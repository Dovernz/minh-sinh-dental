from django import template
from django.utils import timezone
from django.db.models import Sum
import json
from datetime import timedelta

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
        # Tự động dò tìm cột ngày của Booking
        b_fields = [f.name for f in Booking._meta.get_fields()]
        b_date_f = 'created_at' if 'created_at' in b_fields else 'created_on' if 'created_on' in b_fields else 'date_joined'
        stats['bookings'] = str(Booking.objects.filter(**{f"{b_date_f}__date": today}).count())
    except Exception: pass
    
    try:
        from booking.models import Customer
        # Tự động dò tìm cột ngày của Customer
        c_fields = [f.name for f in Customer._meta.get_fields()]
        c_date_f = 'created_at' if 'created_at' in c_fields else 'created_on' if 'created_on' in c_fields else 'date_joined'
        stats['customers'] = str(Customer.objects.filter(**{f"{c_date_f}__date": today}).count())
    except Exception: pass
    return stats

@register.simple_tag
def get_dashboard_charts_json():
    import json
    from datetime import timedelta
    from django.utils import timezone
    from django.utils.timezone import localtime
    
    try:
        from booking.models import Booking, Clinic, TimeSlot
        
        today = localtime(timezone.now()).date()
        dates = [today + timedelta(days=i) for i in range(7)]
        date_strs = [d.strftime('%d/%m') for d in dates]
        full_date_strs = [d.strftime('%Y-%m-%d') for d in dates]
        
        # 1. LẤY CƠ SỞ ĐỘNG 100% TỪ DATABASE
        clinics = list(Clinic.objects.all().order_by('clinic_id'))
        clinic_names = [c.name for c in clinics]
        clinic_ids = {c.name: c.clinic_id for c in clinics}
        if not clinic_names: 
            clinic_names = ["Chưa có cơ sở"] # Phao cứu sinh chống sập biểu đồ nếu DB trống
            clinic_ids = {"Chưa có cơ sở": None}
            
        slots = []
        for s in TimeSlot.objects.all().order_by('start_time'):
            label = f"{s.start_time.strftime('%H:%M')} - {s.end_time.strftime('%H:%M')}"
            slots.append({'id': s.timeslot_id, 'label': label, 'start': s.start_time, 'end': s.end_time})
            
        bookings = Booking.objects.filter(
            start_time__date__gte=today, 
            start_time__date__lte=dates[-1]
        ).exclude(status__in=['Cancelled', 'CANCELLED', 'Đã hủy', 'Canceled'])
        
        bar_series = {c: [0]*7 for c in clinic_names}
        heatmap_dict = {s['id']: {c: 0 for c in clinic_names} for s in slots}
        
        for b in bookings:
            if not b.start_time: continue
            
            local_dt = localtime(b.start_time)
            b_date = local_dt.date()
            b_time = local_dt.time()
            
            if b_date in dates:
                day_idx = dates.index(b_date)
                
                # Trích xuất chính xác tên cơ sở từ DB
                c_name = getattr(b.clinic, 'name', None) if b.clinic else None
                if c_name not in clinic_names:
                    c_name = clinic_names[0]
                
                bar_series[c_name][day_idx] += 1
                
                for s in slots:
                    if s['start'] <= b_time < s['end']:
                        heatmap_dict[s['id']][c_name] += 1
                        break

        bar_json = {
            'categories': date_strs, 
            'series': [{'name': c, 'data': bar_series[c]} for c in clinic_names],
            'full_dates': full_date_strs,
            'clinic_ids': clinic_ids
        }
        
        heatmap_series = []
        for s in reversed(slots):
            heatmap_series.append({
                'name': s['label'],
                'data': [{'x': c, 'y': heatmap_dict[s['id']][c]} for c in clinic_names]
            })
            
        return json.dumps({'error': False, 'bar': bar_json, 'heatmap': heatmap_series})
    except Exception as e:
        return json.dumps({'error': str(e), 'bar': {'categories': [], 'series': []}, 'heatmap': []})