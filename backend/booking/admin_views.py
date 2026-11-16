import decimal
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin, messages
from django.db.models import Q, Sum
from django.db import transaction
from .models import Booking, Billing, Payment

@staff_member_required
def admin_pnr_lookup_view(request):
    title = "Tra Cứu Vé & Booking PNR (Hàng Không)"
    pnr_code = request.GET.get('pnr', '').strip().upper() or request.POST.get('pnr', '').strip().upper()
    
    context = admin.site.each_context(request)
    context.update({
        'title': title,
        'pnr_code': pnr_code,
        'pnr_data': None,
        'error': None,
    })

    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_status':
            booking_id = request.POST.get('booking_id')
            new_status = request.POST.get('status')
            Booking.objects.filter(id=booking_id).update(status=new_status)
            messages.success(request, f"Đã cập nhật trạng thái khách #{booking_id} thành {new_status}")
            return redirect(f"/admin/pnr-lookup/?pnr={pnr_code}")

        elif action == 'group_pay':
            try:
                amount_to_distribute = decimal.Decimal(request.POST.get('amount', '0'))
                method = request.POST.get('payment_method', 'CASH')
                notes = request.POST.get('notes', 'Thanh toán cả đoàn')
                
                bookings_to_pay = Booking.objects.filter(
                    Q(pnr_code__iexact=pnr_code) | Q(group_code__iexact=pnr_code)
                ).select_related('billing')

                with transaction.atomic():
                    remaining = amount_to_distribute
                    for b in bookings_to_pay:
                        if remaining <= 0:
                            break
                        billing = b.billing
                        if billing and billing.total_amount > billing.paid_amount:
                            debt = billing.total_amount - billing.paid_amount
                            pay_value = min(debt, remaining)
                            
                            Payment.objects.create(
                                billing=billing,
                                amount=pay_value,
                                payment_method=method,
                                notes=notes
                            )
                            # Update billing cache if necessary, or let signals handle it
                            billing.paid_amount += pay_value
                            billing.save()
                            remaining -= pay_value

                messages.success(request, f"Đã ghi nhận thanh toán {amount_to_distribute:,.0f} VNĐ cho PNR {pnr_code}")
            except Exception as e:
                messages.error(request, f"Lỗi thanh toán đoàn: {str(e)}")
            return redirect(f"/admin/pnr-lookup/?pnr={pnr_code}")

        elif action == 'individual_pay':
            try:
                booking_id = request.POST.get('booking_id')
                amount = decimal.Decimal(request.POST.get('amount', '0'))
                method = request.POST.get('payment_method', 'CASH')
                notes = request.POST.get('notes', 'Thanh toán lẻ')
                
                booking = Booking.objects.get(id=booking_id)
                if hasattr(booking, 'billing'):
                    Payment.objects.create(
                        billing=booking.billing,
                        amount=amount,
                        payment_method=method,
                        notes=notes
                    )
                    messages.success(request, f"Đã ghi nhận thanh toán {amount:,.0f} VNĐ cho khách #{booking_id}")
            except Exception as e:
                messages.error(request, f"Lỗi thanh toán lẻ: {str(e)}")
            return redirect(f"/admin/pnr-lookup/?pnr={pnr_code}")

    # Query logic
    bookings = Booking.objects.filter(
        Q(pnr_code__iexact=pnr_code) | Q(group_code__iexact=pnr_code)
    ).select_related(
        'customer', 'clinic', 'category', 'billing'
    ).prefetch_related(
        'booking_details__service_detail', 'billing__payments'
    )

    if pnr_code:
        if bookings.exists():
            total_amount = decimal.Decimal('0')
            total_paid = decimal.Decimal('0')
            passengers = []

            for b in bookings:
                b_amount = b.billing.total_amount if hasattr(b, 'billing') else 0
                b_paid = b.billing.paid_amount if hasattr(b, 'billing') else 0
                total_amount += b_amount
                total_paid += b_paid
                
                passengers.append({
                    'booking_id': b.id,
                    'customer_name': b.customer.full_name if b.customer else "N/A",
                    'phone': b.customer.phone if b.customer else "",
                    'services': [str(d.service_detail) for d in b.booking_details.all()],
                    'status': b.status,
                    'individual_amount': b_amount,
                    'individual_paid': b_paid,
                    'individual_balance': b_amount - b_paid,
                    'billing_status': 'PAID' if b_paid >= b_amount and b_amount > 0 else 'PARTIAL' if b_paid > 0 else 'UNPAID'
                })

            remaining_balance = total_amount - total_paid
            percent_paid = (total_paid / total_amount * 100) if total_amount > 0 else 0

            context['pnr_data'] = {
                'pnr_code': pnr_code,
                'clinic': bookings[0].clinic,
                'group_status': "Hoàn tất" if remaining_balance <= 0 else "Còn nợ",
                'total_passengers': bookings.count(),
                'total_amount': total_amount,
                'total_paid': total_paid,
                'remaining_balance': remaining_balance,
                'percent_paid': percent_paid,
                'payment_status': 'Fully Paid' if remaining_balance <= 0 else 'Pending',
                'passengers': passengers
            }
        else:
            context['error'] = f"Không tìm thấy dữ liệu cho mã PNR '{pnr_code}'"

    context['recent_pnrs'] = list(
        Booking.objects.exclude(pnr_code__isnull=True)
        .exclude(pnr_code='')
        .order_by('-booking_id')
        .values_list('pnr_code', flat=True)
        .distinct()[:5]
    )

    return render(request, 'admin/pnr_lookup.html', context)