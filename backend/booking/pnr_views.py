from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .permissions import HasBookingPermission, HasTransactionPermission
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

from .models import (
    Clinic, Customer, ServiceDetail, Booking, 
    BookingDetail, Billing, Payment
)

class PNRLookupAPIView(APIView):
    permission_classes = [IsAuthenticated, HasBookingPermission]

    def get(self, request, pnr_code):
        bookings = Booking.objects.filter(
            Q(pnr_code__iexact=pnr_code) | Q(group_code__iexact=pnr_code)
        ).select_related('customer', 'clinic', 'category').prefetch_related('details__service_detail').order_by('booking_id')

        if not bookings.exists():
            return Response({"error": f"Không tìm thấy mã PNR {pnr_code}"}, status=404)

        first = bookings.first()
        clinic = first.clinic
        passengers_list = []
        
        # Using properties defined in the model
        total_amount = sum(b.total_amount for b in bookings)
        total_paid = sum(b.total_paid for b in bookings)
        remaining_balance = max(Decimal('0'), total_amount - total_paid)
        
        payment_status = 'PAID' if remaining_balance <= 0 and total_amount > 0 else ('PARTIAL' if total_paid > 0 else 'UNPAID')
        
        for b in bookings:
            services = []
            for d in b.details.all():
                sd = d.service_detail
                services.append({
                    "service_id": sd.service_id if sd else None,
                    "name": sd.name if sd else "Dịch vụ",
                    "code": sd.code if sd else "",
                    "price": float(d.actual_price or 0),
                    "quantity": d.quantity or 1,
                    "total": float((d.actual_price or 0) * (d.quantity or 1))
                })
            
            billing = getattr(b, 'billing', None)
            st_local = timezone.localtime(b.start_time) if (b.start_time and timezone.is_aware(b.start_time)) else b.start_time
            et_local = timezone.localtime(b.end_time) if (b.end_time and timezone.is_aware(b.end_time)) else b.end_time
            passengers_list.append({
                "booking_id": b.booking_id,
                "status": b.status,
                "start_time": st_local.strftime("%Y-%m-%d %H:%M") if st_local else None,
                "end_time": et_local.strftime("%Y-%m-%d %H:%M") if et_local else None,
                "estimated_duration": b.estimated_duration,
                "notes": b.notes,
                "customer": {
                    "customer_id": b.customer.customer_id,
                    "patient_code": b.customer.patient_code,
                    "name": b.customer.name,
                    "phone": b.customer.phone,
                    "email": b.customer.email,
                    "dob": b.customer.customer_dob.strftime("%Y-%m-%d") if b.customer.customer_dob else None,
                    "gender": b.customer.gender,
                    "address": b.customer.address
                },
                "category": b.category.name if b.category else None,
                "services": services,
                "individual_amount": float(b.total_amount),
                "individual_paid": float(b.total_paid),
                "individual_balance": float(b.remaining_balance),
                "billing_id": billing.billing_id if billing else None,
                "billing_status": billing.status if billing else 'UNPAID'
            })

        return Response({
            "pnr_code": pnr_code,
            "clinic": {
                "id": clinic.clinic_id,
                "name": clinic.name,
                "address": clinic.address,
                "hotline": clinic.hotline,
                "total_chairs": clinic.total_chairs
            } if clinic else None,
            "group_status": first.get_group_status(),
            "total_passengers": bookings.count(),
            "total_amount": float(total_amount),
            "total_paid": float(total_paid),
            "remaining_balance": float(remaining_balance),
            "payment_status": payment_status,
            "passengers": passengers_list
        })

class PNRPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated, HasTransactionPermission]

    @transaction.atomic
    def post(self, request, pnr_code=None):
        pnr_code = pnr_code or request.data.get('pnr_code')
        amount_to_distribute = Decimal(str(request.data.get('amount', 0)))
        payment_method = request.data.get('payment_method', 'CASH')
        notes = request.data.get('notes', '')

        if amount_to_distribute <= 0:
            return Response({"error": "Số tiền thanh toán phải lớn hơn 0"}, status=400)

        bookings = Booking.objects.filter(
            Q(pnr_code__iexact=pnr_code) | Q(group_code__iexact=pnr_code)
        ).exclude(status__in=['Cancelled', 'cancelled', 'Đã hủy', 'CANCELLED']).order_by('booking_id')

        if not bookings.exists():
            return Response({"error": f"Không tìm thấy PNR {pnr_code}"}, status=404)
        
        remaining_to_pay = amount_to_distribute
        payment_details = []

        for b in bookings:
            if remaining_to_pay <= 0:
                break
            
            billing = getattr(b, 'billing', None)
            if not billing:
                billing = Billing.objects.create(
                    booking=b, 
                    clinic=b.clinic,
                    subtotal=b.total_amount, 
                    final_total=b.total_amount,
                    status='UNPAID', 
                    notes=notes
                )
            
            paid_so_far = billing.total_paid
            balance_due = max(Decimal('0'), billing.final_total - paid_so_far)

            if balance_due > 0:
                pay_amt = min(remaining_to_pay, balance_due)
                rem_after = max(Decimal('0'), balance_due - pay_amt)
                
                Payment.objects.create(
                    billing=billing, 
                    amount=pay_amt, 
                    payment_method=payment_method,
                    total_billing=billing.final_total, 
                    amount_remain=rem_after
                )
                
                remaining_to_pay -= pay_amt
                
                if rem_after <= 0:
                    billing.status = 'PAID'
                    b.status = 'Completed'
                    b.save(update_fields=['status'])
                else:
                    billing.status = 'INSTALLMENT'
                
                billing.save(update_fields=['status'])
                
                payment_details.append({
                    "booking_id": b.booking_id,
                    "paid_amount": float(pay_amt),
                    "billing_status": billing.status
                })

        total_pnr_amount = sum(b.total_amount for b in bookings)
        total_pnr_paid = sum(b.total_paid for b in bookings)
        new_rem = max(Decimal('0'), total_pnr_amount - total_pnr_paid)

        return Response({
            "status": "success",
            "pnr_code": pnr_code,
            "total_paid_now": float(amount_to_distribute - remaining_to_pay),
            "remaining_balance": float(new_rem),
            "details": payment_details
        })

class IndividualPaymentAPIView(APIView):
    permission_classes = [IsAuthenticated, HasTransactionPermission]

    @transaction.atomic
    def post(self, request):
        booking_id = request.data.get('booking_id')
        amount = Decimal(str(request.data.get('amount', 0)))
        payment_method = request.data.get('payment_method', 'CASH')
        notes = request.data.get('notes', '')

        if not booking_id:
            return Response({"error": "Thiếu booking_id"}, status=400)

        b = get_object_or_404(Booking, pk=booking_id)
        billing = getattr(b, 'billing', None)
        
        if not billing:
            billing = Billing.objects.create(
                booking=b, 
                clinic=b.clinic,
                subtotal=b.total_amount, 
                final_total=b.total_amount,
                status='UNPAID', 
                notes=notes
            )
        
        paid_so_far = billing.total_paid
        rem_after = max(Decimal('0'), billing.final_total - (paid_so_far + amount))
        
        Payment.objects.create(
            billing=billing, 
            amount=amount, 
            payment_method=payment_method,
            total_billing=billing.final_total, 
            amount_remain=rem_after
        )
        
        if rem_after <= 0:
            billing.status = 'PAID'
            b.status = 'Completed'
            b.save(update_fields=['status'])
        else:
            billing.status = 'INSTALLMENT'
        
        billing.save(update_fields=['status'])

        return Response({
            "status": "success",
            "booking_id": b.booking_id,
            "billing_id": billing.billing_id,
            "paid_amount": float(amount),
            "remaining_balance": float(rem_after),
            "billing_status": billing.status
        })

class PNRPassengerStatusUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated, HasBookingPermission]

    def post(self, request, pnr_code, booking_id):
        new_status = request.data.get('status')
        b = get_object_or_404(Booking, pk=booking_id)
        b.status = new_status
        b.save(update_fields=['status'])
        
        return Response({
            "status": "success",
            "booking_id": b.booking_id,
            "new_status": b.status,
            "group_status": b.get_group_status()
        })

class CapacityCheckAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        clinic_id = request.query_params.get('clinic_id')
        date_str = request.query_params.get('date')
        start_time_str = request.query_params.get('start_time')
        passenger_count = int(request.query_params.get('passenger_count', 1))
        duration = int(request.query_params.get('duration', 30))
        
        clinic = get_object_or_404(Clinic, pk=clinic_id)
        
        try:
            dt_obj = datetime.strptime(f"{date_str} {start_time_str}", "%Y-%m-%d %H:%M")
        except (ValueError, TypeError):
            return Response({"error": "Định dạng ngày hoặc giờ không hợp lệ (YYYY-MM-DD HH:MM)"}, status=400)

        from .schedule_services import get_slot_capacity
        cap = get_slot_capacity(
            clinic=clinic,
            target_date=dt_obj.date(),
            start_time_obj=dt_obj.time(),
            duration_minutes=duration,
            requested_count=passenger_count,
        )

        return Response({
            "clinic_id": clinic.clinic_id,
            "clinic_name": clinic.name,
            "date": date_str,
            "start_time": start_time_str,
            **cap,
        })