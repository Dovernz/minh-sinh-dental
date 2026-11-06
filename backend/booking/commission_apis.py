from django.views import View
from django.http import JsonResponse
from booking.models import Booking, BookingDetail, Employee, CommissionRate, Payment, Billing
from django.db.models import Sum, Q, F
from django.utils.dateparse import parse_date
from django.utils import timezone

def get_commission_rates():
    return list(CommissionRate.objects.all())

def get_rate_for_date(target_date, rates):
    if not target_date:
        target_date = timezone.now().date()
        
    rates_sorted = sorted(rates, key=lambda x: x.start_date, reverse=True)
    for r in rates_sorted:
        if r.start_date <= target_date:
            if not r.end_date or target_date <= r.end_date:
                return r
    if rates_sorted:
        return rates_sorted[-1]
    return None

def calculate_commissions(detail, rates):
    consulting_val = 0
    performing_val = 0
    booking_date = None
    if detail.booking:
        if detail.booking.created_on:
            booking_date = detail.booking.created_on.date()
        elif detail.booking.start_time:
            booking_date = detail.booking.start_time.date()
    rate_obj = get_rate_for_date(booking_date, rates)
    if not rate_obj:
        return 0, 0
    qty = detail.quantity or 1
    total_price = float(detail.actual_price or 0) * float(qty)
    if detail.consulting_doctor and detail.consulting_doctor.contract_type == 'Part-time':
        consulting_val = total_price * float(rate_obj.consulting_rate_percent) / 100.0
    if detail.performing_doctor and detail.performing_doctor.contract_type == 'Part-time':
        performing_val = total_price * float(rate_obj.performing_rate_percent) / 100.0
    return consulting_val, performing_val

def extract_commission_items(start_date=None, end_date=None, doctor_id=None, calc_mode='payment'):
    """
    Trích xuất toàn bộ các khoản hoa hồng của Bác sĩ Part-time:
    - calc_mode == 'payment' (Mặc định - Thực thu theo từng đợt thanh toán):
        Hoa hồng được chia tách và tính toán theo từng phiếu thu thực tế (Payment).
        Cho phép 1 ca khám có hóa đơn lớn được trả thành nhiều lần thì hoa hồng sẽ
        được bóc tách trả tương ứng theo từng lần thu tiền.
    - calc_mode == 'booking' (Theo doanh số ca khám - 1 cục ban đầu):
        Hoa hồng tính trên tổng giá trị dịch vụ của ca khám khi hoàn tất.

    QUY TẮC PHÂN TÁCH BÁC SĨ HỢP ĐỒNG (FULL-TIME) VS PART-TIME:
    - Bác sĩ Hợp đồng (Full-time): Nhận lương cứng, TUYỆT ĐỐI KHÔNG tính hoa hồng (0 đ).
    - Bác sĩ Part-time: ĐƯỢC TÍNH hoa hồng theo tỷ lệ tại thời điểm phát sinh (Thực hiện/Tư vấn).
    - Nếu 1 ca có cả BS Full-time và BS Part-time cùng tham gia:
        Chỉ tính hoa hồng cho phần việc của BS Part-time.
    """
    rates = get_commission_rates()
    items = []
    
    d_start = parse_date(start_date) if start_date else None
    d_end = parse_date(end_date) if end_date else None

    if calc_mode == 'payment':
        # 1. Thu thập hoa hồng theo từng đợt thanh toán thực tế (Payment)
        payment_qs = Payment.objects.select_related(
            'billing', 'billing__booking', 'billing__booking__customer'
        ).prefetch_related(
            'billing__booking__details',
            'billing__booking__details__consulting_doctor',
            'billing__booking__details__performing_doctor',
            'billing__booking__details__service_detail'
        ).order_by('created_at')

        if d_start:
            payment_qs = payment_qs.filter(created_at__date__gte=d_start)
        if d_end:
            payment_qs = payment_qs.filter(created_at__date__lte=d_end)

        processed_booking_ids = set()

        for pay in payment_qs:
            if not pay.billing or not pay.billing.booking:
                continue
            
            b = pay.billing.booking
            processed_booking_ids.add(b.booking_id)
            pay_date = pay.created_at.date()
            rate_obj = get_rate_for_date(pay_date, rates)
            if not rate_obj:
                continue

            details = list(b.details.all())
            if not details:
                continue

            total_service_sum = sum(float(d.actual_price or 0) * (d.quantity or 1) for d in details)
            pay_amount = float(pay.amount or 0)
            if pay_amount <= 0:
                continue

            for d in details:
                d_qty = d.quantity or 1
                d_total = float(d.actual_price or 0) * float(d_qty)
                weight = (d_total / total_service_sum) if total_service_sum > 0 else (1.0 / len(details))
                allocated_revenue = pay_amount * weight

                customer_name = b.customer.name if b.customer else 'Khách vãng lai'
                service_name = d.service_detail.name if d.service_detail else 'Dịch vụ điều trị'
                date_str = pay.created_at.strftime('%Y-%m-%d %H:%M')

                # Tư vấn: CHỈ tính nếu là Bác sĩ Part-time
                if d.consulting_doctor and d.consulting_doctor.contract_type == 'Part-time':
                    if doctor_id is None or d.consulting_doctor_id == doctor_id:
                        c_rate = float(rate_obj.consulting_rate_percent)
                        c_val = allocated_revenue * c_rate / 100.0
                        if c_val > 0:
                            items.append({
                                'doctor_id': d.consulting_doctor_id,
                                'doctor_name': d.consulting_doctor.full_name,
                                'booking_id': b.booking_id,
                                'payment_id': pay.payment_id,
                                'date': date_str,
                                'customer': customer_name,
                                'service': service_name,
                                'role': 'Consulting',
                                'actual_price': allocated_revenue,
                                'commission': c_val,
                                'rate_percent': c_rate,
                                'payment_note': f"Đợt thu #{pay.payment_id}"
                            })

                # Thực hiện: CHỈ tính nếu là Bác sĩ Part-time
                if d.performing_doctor and d.performing_doctor.contract_type == 'Part-time':
                    if doctor_id is None or d.performing_doctor_id == doctor_id:
                        p_rate = float(rate_obj.performing_rate_percent)
                        p_val = allocated_revenue * p_rate / 100.0
                        if p_val > 0:
                            items.append({
                                'doctor_id': d.performing_doctor_id,
                                'doctor_name': d.performing_doctor.full_name,
                                'booking_id': b.booking_id,
                                'payment_id': pay.payment_id,
                                'date': date_str,
                                'customer': customer_name,
                                'service': service_name,
                                'role': 'Performing',
                                'actual_price': allocated_revenue,
                                'commission': p_val,
                                'rate_percent': p_rate,
                                'payment_note': f"Đợt thu #{pay.payment_id}"
                            })

        # 2. Bổ sung các ca khám Completed nhưng CHƯA có phiếu Payment nào (fallback tương thích)
        unpaid_details = BookingDetail.objects.filter(
            booking__status='Completed'
        ).exclude(
            booking_id__in=processed_booking_ids
        ).select_related('booking', 'booking__customer', 'service_detail', 'consulting_doctor', 'performing_doctor')

        if d_start:
            unpaid_details = unpaid_details.filter(
                Q(booking__created_on__date__gte=d_start) | (Q(booking__created_on__isnull=True) & Q(booking__start_time__date__gte=d_start))
            )
        if d_end:
            unpaid_details = unpaid_details.filter(
                Q(booking__created_on__date__lte=d_end) | (Q(booking__created_on__isnull=True) & Q(booking__start_time__date__lte=d_end))
            )

        for d in unpaid_details:
            b = d.booking
            b_date = b.created_on.date() if b.created_on else (b.start_time.date() if b.start_time else timezone.now().date())
            rate_obj = get_rate_for_date(b_date, rates)
            if not rate_obj:
                continue

            d_qty = d.quantity or 1
            d_total = float(d.actual_price or 0) * float(d_qty)
            customer_name = b.customer.name if b.customer else 'Khách vãng lai'
            service_name = d.service_detail.name if d.service_detail else 'Dịch vụ điều trị'
            date_str = (b.created_on or b.start_time).strftime('%Y-%m-%d %H:%M') if (b.created_on or b.start_time) else None

            # Tư vấn (chỉ Part-time)
            if d.consulting_doctor and d.consulting_doctor.contract_type == 'Part-time':
                if doctor_id is None or d.consulting_doctor_id == doctor_id:
                    c_rate = float(rate_obj.consulting_rate_percent)
                    c_val = d_total * c_rate / 100.0
                    if c_val > 0:
                        items.append({
                            'doctor_id': d.consulting_doctor_id,
                            'doctor_name': d.consulting_doctor.full_name,
                            'booking_id': b.booking_id,
                            'payment_id': None,
                            'date': date_str,
                            'customer': customer_name,
                            'service': service_name,
                            'role': 'Consulting',
                            'actual_price': d_total,
                            'commission': c_val,
                            'rate_percent': c_rate,
                            'payment_note': "Toàn bộ ca khám"
                        })

            # Thực hiện (chỉ Part-time)
            if d.performing_doctor and d.performing_doctor.contract_type == 'Part-time':
                if doctor_id is None or d.performing_doctor_id == doctor_id:
                    p_rate = float(rate_obj.performing_rate_percent)
                    p_val = d_total * p_rate / 100.0
                    if p_val > 0:
                        items.append({
                            'doctor_id': d.performing_doctor_id,
                            'doctor_name': d.performing_doctor.full_name,
                            'booking_id': b.booking_id,
                            'payment_id': None,
                            'date': date_str,
                            'customer': customer_name,
                            'service': service_name,
                            'role': 'Performing',
                            'actual_price': d_total,
                            'commission': p_val,
                            'rate_percent': p_rate,
                            'payment_note': "Toàn bộ ca khám"
                        })

    else:
        # calc_mode == 'booking' (Theo toàn bộ ca khám)
        details = BookingDetail.objects.filter(
            booking__status='Completed'
        ).select_related('booking', 'booking__customer', 'service_detail', 'consulting_doctor', 'performing_doctor')

        if d_start:
            details = details.filter(
                Q(booking__created_on__date__gte=d_start) | (Q(booking__created_on__isnull=True) & Q(booking__start_time__date__gte=d_start))
            )
        if d_end:
            details = details.filter(
                Q(booking__created_on__date__lte=d_end) | (Q(booking__created_on__isnull=True) & Q(booking__start_time__date__lte=d_end))
            )

        for d in details:
            b = d.booking
            b_date = b.created_on.date() if b.created_on else (b.start_time.date() if b.start_time else timezone.now().date())
            rate_obj = get_rate_for_date(b_date, rates)
            if not rate_obj:
                continue

            d_qty = d.quantity or 1
            d_total = float(d.actual_price or 0) * float(d_qty)
            customer_name = b.customer.name if b.customer else 'Khách vãng lai'
            service_name = d.service_detail.name if d.service_detail else 'Dịch vụ điều trị'
            date_str = (b.created_on or b.start_time).strftime('%Y-%m-%d %H:%M') if (b.created_on or b.start_time) else None

            if d.consulting_doctor and d.consulting_doctor.contract_type == 'Part-time':
                if doctor_id is None or d.consulting_doctor_id == doctor_id:
                    c_rate = float(rate_obj.consulting_rate_percent)
                    c_val = d_total * c_rate / 100.0
                    if c_val > 0:
                        items.append({
                            'doctor_id': d.consulting_doctor_id,
                            'doctor_name': d.consulting_doctor.full_name,
                            'booking_id': b.booking_id,
                            'payment_id': None,
                            'date': date_str,
                            'customer': customer_name,
                            'service': service_name,
                            'role': 'Consulting',
                            'actual_price': d_total,
                            'commission': c_val,
                            'rate_percent': c_rate,
                            'payment_note': "Toàn bộ ca khám"
                        })

            if d.performing_doctor and d.performing_doctor.contract_type == 'Part-time':
                if doctor_id is None or d.performing_doctor_id == doctor_id:
                    p_rate = float(rate_obj.performing_rate_percent)
                    p_val = d_total * p_rate / 100.0
                    if p_val > 0:
                        items.append({
                            'doctor_id': d.performing_doctor_id,
                            'doctor_name': d.performing_doctor.full_name,
                            'booking_id': b.booking_id,
                            'payment_id': None,
                            'date': date_str,
                            'customer': customer_name,
                            'service': service_name,
                            'role': 'Performing',
                            'actual_price': d_total,
                            'commission': p_val,
                            'rate_percent': p_rate,
                            'payment_note': "Toàn bộ ca khám"
                        })

    return items


class CommissionOverviewAPIView(View):
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        calc_mode = request.GET.get('mode', 'payment')
        
        items = extract_commission_items(start_date=start_date, end_date=end_date, calc_mode=calc_mode)
        
        doctors = {}
        for item in items:
            doc_id = item['doctor_id']
            if doc_id not in doctors:
                doctors[doc_id] = {
                    'id': doc_id,
                    'name': item['doctor_name'],
                    'total_consulting': 0,
                    'total_performing': 0,
                    'total': 0
                }
            if item['role'] == 'Consulting':
                doctors[doc_id]['total_consulting'] += item['commission']
            elif item['role'] == 'Performing':
                doctors[doc_id]['total_performing'] += item['commission']
            doctors[doc_id]['total'] += item['commission']
            
        result = [v for v in doctors.values() if v['total'] > 0]
        return JsonResponse(result, safe=False)


class CommissionDetailAPIView(View):
    def get(self, request, doctor_id):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        calc_mode = request.GET.get('mode', 'payment')
        
        items = extract_commission_items(
            start_date=start_date, end_date=end_date, doctor_id=doctor_id, calc_mode=calc_mode
        )
        return JsonResponse(items, safe=False)
