from django.views import View
from django.http import JsonResponse
from booking.models import BookingDetail, Employee, CommissionRate
from django.db.models import Sum, Q, F
from django.utils.dateparse import parse_date

def get_commission_rates():
    return list(CommissionRate.objects.all())

def calculate_commissions(detail, rates):
    consulting_val = 0
    performing_val = 0
    
    booking_date = detail.booking.created_on.date() if detail.booking and detail.booking.created_on else None
    
    if not booking_date:
        return 0, 0
        
    rate_obj = None
    # Sort rates by start_date descending to find the latest applicable rate
    rates_sorted = sorted(rates, key=lambda x: x.start_date, reverse=True)
    for r in rates_sorted:
        if r.start_date <= booking_date:
            # If the rate has a specific end_date, check it. Otherwise it's valid indefinitely.
            if not r.end_date or booking_date <= r.end_date:
                rate_obj = r
                break
            
    if not rate_obj:
        return 0, 0
        
    if detail.consulting_doctor_id and detail.consulting_doctor.contract_type == 'Part-time':
        consulting_val = float(detail.actual_price or 0) * float(rate_obj.consulting_rate_percent) / 100
        
    if detail.performing_doctor_id and detail.performing_doctor.contract_type == 'Part-time':
        performing_val = float(detail.actual_price or 0) * float(rate_obj.performing_rate_percent) / 100
        
    return consulting_val, performing_val


class CommissionOverviewAPIView(View):
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        qs = BookingDetail.objects.filter(booking__status='Completed').select_related('consulting_doctor', 'performing_doctor', 'booking')
        if start_date:
            qs = qs.filter(booking__created_on__gte=parse_date(start_date))
        if end_date:
            qs = qs.filter(booking__created_on__lte=parse_date(end_date))
            
        doctors = {}
        rates = get_commission_rates()
        
        for d in qs:
            c_val, p_val = calculate_commissions(d, rates)
            
            # Consulting
            if d.consulting_doctor_id:
                doc_id = d.consulting_doctor_id
                if doc_id not in doctors:
                    doctors[doc_id] = {'id': doc_id, 'name': d.consulting_doctor.full_name, 'total_consulting': 0, 'total_performing': 0, 'total': 0}
                doctors[doc_id]['total_consulting'] += c_val
                doctors[doc_id]['total'] += c_val
                
            # Performing
            if d.performing_doctor_id:
                doc_id = d.performing_doctor_id
                if doc_id not in doctors:
                    doctors[doc_id] = {'id': doc_id, 'name': d.performing_doctor.full_name, 'total_consulting': 0, 'total_performing': 0, 'total': 0}
                doctors[doc_id]['total_performing'] += p_val
                doctors[doc_id]['total'] += p_val
                
        result = [v for v in doctors.values() if v['total'] > 0]
        return JsonResponse(result, safe=False)


class CommissionDetailAPIView(View):
    def get(self, request, doctor_id):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        qs = BookingDetail.objects.filter(booking__status='Completed').filter(
            Q(consulting_doctor_id=doctor_id) | Q(performing_doctor_id=doctor_id)
        ).select_related('booking', 'booking__customer', 'service_detail', 'consulting_doctor', 'performing_doctor')
        
        if start_date:
            qs = qs.filter(booking__created_on__gte=parse_date(start_date))
        if end_date:
            qs = qs.filter(booking__created_on__lte=parse_date(end_date))
            
        data = []
        rates = get_commission_rates()
        
        for d in qs:
            date_str = d.booking.created_on.strftime('%Y-%m-%d %H:%M') if d.booking.created_on else None
            customer_name = d.booking.customer.name if d.booking.customer else ''
            service_name = d.service_detail.name if d.service_detail else ''
            
            c_val, p_val = calculate_commissions(d, rates)
            
            if d.consulting_doctor_id == doctor_id and c_val > 0:
                data.append({
                    'booking_id': d.booking_id,
                    'date': date_str,
                    'customer': customer_name,
                    'service': service_name,
                    'role': 'Consulting',
                    'actual_price': float(d.actual_price or 0),
                    'commission': c_val
                })
                
            if d.performing_doctor_id == doctor_id and p_val > 0:
                data.append({
                    'booking_id': d.booking_id,
                    'date': date_str,
                    'customer': customer_name,
                    'service': service_name,
                    'role': 'Performing',
                    'actual_price': float(d.actual_price or 0),
                    'commission': p_val
                })
                
        return JsonResponse(data, safe=False)
