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
        stats['bookings'] = str(Booking.objects.filter(created_at__date=today).count())
    except Exception: pass
    
    try:
        from booking.models import Customer
        stats['customers'] = str(Customer.objects.filter(created_at__date=today).count())
    except Exception: pass
    return stats

@register.simple_tag
def get_dashboard_charts_json():
    import json
    from datetime import timedelta
    from django.utils import timezone
    
    today = timezone.now().date()
    dates = [today + timedelta(days=i) for i in range(7)]
    date_strs = [d.strftime('%d/%m') for d in dates]

    try:
        from booking.models import Booking, Clinic, TimeSlot
        
        # TRUY VẤN THEO start_time (MODEL CỦA BẠN KHÔNG CÓ timeslot FOREIGN KEY)
        bookings = Booking.objects.filter(start_time__date__gte=today, start_time__date__lte=dates[-1])
        
        # 1. Lấy Cơ sở
        clinics = []
        try:
            clinics = list(Clinic.objects.all().order_by('clinic_id').values_list('name', flat=True))
        except: pass
        if not clinics: clinics = ["Cơ sở 1", "Cơ sở 2"]
        
        # 2. Lấy TOÀN BỘ TimeSlot 30 phút theo thứ tự chuẩn
        slot_names = []
        try:
            qs = TimeSlot.objects.all().order_by('start_time')
            slot_names = [s.start_time.strftime('%H:%M') for s in qs]
        except: pass
        if not slot_names:
            slot_names = [f"{str(i).zfill(2)}:00" for i in range(8, 19)]
        
        bar_series = {c: [0]*7 for c in clinics}
        heatmap_dict = {s: {c: 0 for c in clinics} for s in slot_names}
        
        for b in bookings:
            try:
                b_date = getattr(b, 'start_time')
                if not b_date: continue
                
                just_date = b_date.date() if hasattr(b_date, 'date') else b_date
                just_time = b_date.time() if hasattr(b_date, 'time') else None
                
                if just_date in dates:
                    day_idx = dates.index(just_date)
                    c_obj = getattr(b, 'clinic', None)
                    c_name = getattr(c_obj, 'name', str(c_obj)) if c_obj else None
                    if c_name not in clinics: c_name = clinics[0]
                    
                    if c_name in bar_series: bar_series[c_name][day_idx] += 1
                    
                    if just_time:
                        hour_str = just_time.strftime('%H:%M')
                        minute = "30" if just_time.minute >= 30 else "00"
                        approx_slot = f"{str(just_time.hour).zfill(2)}:{minute}"
                        
                        t_name = hour_str if hour_str in heatmap_dict else approx_slot
                        if t_name in heatmap_dict: 
                            heatmap_dict[t_name][c_name] += 1
            except: pass

        bar_json = {'categories': date_strs, 'series': [{'name': c, 'data': bar_series[c]} for c in clinics]}
        
        heatmap_series = []
        # Đảo ngược danh sách vì ApexCharts vẽ từ dưới lên trên
        for t_name in reversed(slot_names):
            heatmap_series.append({
                'name': t_name,
                'data': [{'x': c, 'y': heatmap_dict[t_name][c]} for c in clinics]
            })
            
        return json.dumps({'error': False, 'bar': bar_json, 'heatmap': heatmap_series})
    except Exception as e:
        return json.dumps({'error': str(e), 'bar': {'categories': date_strs, 'series': []}, 'heatmap': []})