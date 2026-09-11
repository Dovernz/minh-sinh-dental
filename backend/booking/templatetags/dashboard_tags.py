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
    from datetime import timedelta, datetime, time
    from django.utils import timezone
    
    today = timezone.now().date()
    dates = [today + timedelta(days=i) for i in range(7)]
    date_strs = [d.strftime('%d/%m') for d in dates]

    try:
        from booking.models import Booking, Clinic, TimeSlot
        
        # 1. LẤY DANH SÁCH CƠ SỞ
        clinics = list(Clinic.objects.all().order_by('clinic_id').values_list('name', flat=True))
        if not clinics: clinics = ["Cơ sở 1", "Cơ sở 2"]
        
        # 2. LẤY VÀ CẤU TRÚC LẠI BẢNG TIMESLOT (Tạo khoảng so sánh Start - End)
        slots = []
        qs = TimeSlot.objects.all().order_by('start_time')
        for s in qs:
            s_start = getattr(s, 'start_time', getattr(s, 'time', None))
            s_end = getattr(s, 'end_time', None)
            
            # Format nhãn hiển thị trực quan (VD: 08:00 - 08:30)
            if s_start and s_end: label = f"{s_start.strftime('%H:%M')} - {s_end.strftime('%H:%M')}"
            else: label = str(getattr(s, 'name', getattr(s, 'time', str(s))))
            
            slots.append({'id': getattr(s, 'timeslot_id', getattr(s, 'id', None)), 'label': label, 'start': s_start, 'end': s_end})
            
        # 3. TRUY VẤN BOOKING
        # Bắt cứng vào `start_time` vì Model Booking sử dụng `start_time` (DateTimeField) thay vì ForeignKey timeslot
        date_f = 'start_time'
        time_f = 'start_time'
        clinic_f = 'clinic'
        
        bookings = Booking.objects.filter(start_time__date__gte=today, start_time__date__lte=dates[-1])
        
        bar_series = {c: [0]*7 for c in clinics}
        heatmap_dict = {s['id']: {c: 0 for c in clinics} for s in slots if s['id'] is not None}
        
        # 4. THUẬT TOÁN ĐỐI CHIẾU THỜI GIAN THỰC (TIME-MATCHING)
        for b in bookings:
            try:
                b_datetime = getattr(b, date_f, getattr(b, 'created_at', None))
                if not b_datetime: continue
                
                b_date = b_datetime.date() if hasattr(b_datetime, 'date') else b_datetime
                
                if b_date in dates:
                    day_idx = dates.index(b_date)
                    
                    c_obj = getattr(b, clinic_f, None)
                    c_name = getattr(c_obj, 'name', str(c_obj)) if c_obj else clinics[0]
                    if c_name not in clinics: c_name = clinics[0]
                    
                    bar_series[c_name][day_idx] += 1
                    
                    # Bóc tách giờ khám thực tế của khách hàng
                    b_time = b_datetime.time() if hasattr(b_datetime, 'time') else b_datetime
                    
                    # Đối chiếu giờ khám rơi vào khe TimeSlot nào
                    matched_id = None
                    if b_time:
                        for s in slots:
                            if s['start'] and s['end']:
                                if s['start'] <= b_time < s['end']:
                                    matched_id = s['id']
                                    break
                            elif s['start']:
                                if s['start'] == b_time:
                                    matched_id = s['id']
                                    break
                                    
                    # Dự phòng: Nếu Booking có trực tiếp FK TimeSlot
                    if not matched_id and hasattr(b, 'time_slot') and getattr(b, 'time_slot'): matched_id = getattr(b.time_slot, 'timeslot_id', getattr(b.time_slot, 'id', None))
                    elif not matched_id and hasattr(b, 'timeslot') and getattr(b, 'timeslot'): matched_id = getattr(b.timeslot, 'timeslot_id', getattr(b.timeslot, 'id', None))
                        
                    # Bơm dữ liệu vào Heatmap
                    if matched_id and matched_id in heatmap_dict:
                        heatmap_dict[matched_id][c_name] += 1
            except Exception as inner_e: pass

        bar_json = {'categories': date_strs, 'series': [{'name': c, 'data': bar_series[c]} for c in clinics]}
        
        heatmap_series = []
        for s in reversed(slots):
            if s['id'] is not None:
                heatmap_series.append({
                    'name': s['label'],
                    'data': [{'x': c, 'y': heatmap_dict[s['id']][c]} for c in clinics]
                })
            
        return json.dumps({'error': False, 'bar': bar_json, 'heatmap': heatmap_series})
    except Exception as e:
        return json.dumps({'error': str(e), 'bar': {'categories': date_strs, 'series': []}, 'heatmap': []})