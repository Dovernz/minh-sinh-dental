import decimal
from decimal import Decimal
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from .permissions import has_booking_perm, has_transaction_perm
from django.contrib import admin, messages
from django.db.models import Q
from django.db import transaction
from .models import Booking, Billing, Payment, BookingStatusHistory


@staff_member_required
def admin_pnr_lookup_view(request):
    if not has_booking_perm(request.user):
        raise PermissionDenied
    pnr_code = request.GET.get('pnr', '').strip()
    if request.method == 'POST':
        pnr_code = request.POST.get('pnr', pnr_code).strip()
        action = request.POST.get('action', '').strip().lower()
        is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.POST.get('format') == 'json'

        try:
            with transaction.atomic():
                if action in ['pay_all', 'group_pay']:
                    if not has_transaction_perm(request.user):
                        if is_ajax:
                            return JsonResponse({'status': 'error', 'message': 'Bạn không có quyền thu tiền / thanh toán.'}, status=403)
                        raise PermissionDenied
                    if not pnr_code:
                        if is_ajax:
                            return JsonResponse({'status': 'error', 'message': 'Thiếu mã PNR hoặc mã đoàn.'}, status=400)
                        messages.error(request, 'Thiếu mã PNR hoặc mã đoàn.')
                        return redirect('/admin/pnr-lookup/')

                    bookings = Booking.objects.filter(
                        Q(pnr_code__iexact=pnr_code) | Q(group_code__iexact=pnr_code)
                    )
                    
                    if not bookings.exists():
                        if is_ajax:
                            return JsonResponse({'status': 'error', 'message': f'Không tìm thấy đoàn khách với mã {pnr_code}'}, status=404)
                        messages.error(request, f'Không tìm thấy đoàn khách với mã {pnr_code}')
                        return redirect(f'/admin/pnr-lookup/?pnr={pnr_code}')

                    payment_method = request.POST.get('payment_method', 'CASH')

                    for b in bookings:
                        remaining = b.remaining_balance
                        if remaining > 0:
                            billing, _ = Billing.objects.get_or_create(
                                booking=b,
                                defaults={
                                    'subtotal': b.total_amount,
                                    'final_total': b.total_amount,
                                    'clinic': b.clinic
                                }
                            )
                            Payment.objects.create(
                                billing=billing,
                                amount=remaining,
                                payment_method=payment_method,
                                total_billing=billing.final_total,
                                amount_remain=Decimal('0')
                            )
                            billing.status = 'PAID'
                            billing.save(update_fields=['status'])

                    msg = f'Đã thanh toán thành công toàn bộ đoàn {pnr_code}'
                    if is_ajax:
                        return JsonResponse({'status': 'success', 'message': msg})
                    messages.success(request, msg)
                    return redirect(f'/admin/pnr-lookup/?pnr={pnr_code}')

                elif action in ['pay_item', 'individual_pay']:
                    booking_id = request.POST.get('booking_id')
                    if not booking_id:
                        if is_ajax:
                            return JsonResponse({'status': 'error', 'message': 'Thiếu mã booking.'}, status=400)
                        messages.error(request, 'Thiếu mã booking.')
                        return redirect(f'/admin/pnr-lookup/?pnr={pnr_code}')

                    try:
                        b = Booking.objects.get(booking_id=booking_id)
                    except Booking.DoesNotExist:
                        if is_ajax:
                            return JsonResponse({'status': 'error', 'message': 'Không tìm thấy thông tin đặt lịch.'}, status=404)
                        messages.error(request, 'Không tìm thấy thông tin đặt lịch.')
                        return redirect(f'/admin/pnr-lookup/?pnr={pnr_code}')

                    amt_val = request.POST.get('amount')
                    pay_amount = Decimal(amt_val) if amt_val and Decimal(amt_val) > 0 else b.remaining_balance
                    pay_amount = min(pay_amount, b.remaining_balance)

                    if pay_amount > 0:
                        billing, _ = Billing.objects.get_or_create(
                            booking=b,
                            defaults={
                                'subtotal': b.total_amount,
                                'final_total': b.total_amount,
                                'clinic': b.clinic
                            }
                        )
                        new_remain = max(Decimal('0'), billing.final_total - billing.total_paid - pay_amount)
                        Payment.objects.create(
                            billing=billing,
                            amount=pay_amount,
                            payment_method=request.POST.get('payment_method', 'CASH'),
                            total_billing=billing.final_total,
                            amount_remain=new_remain
                        )
                        if new_remain <= 0:
                            billing.status = 'PAID'
                        elif billing.total_paid > 0:
                            billing.status = 'INSTALLMENT'
                        billing.save(update_fields=['status'])

                    msg = f'Đã thu {pay_amount:,.0f} VNĐ cho khách #{b.booking_id}'
                    if is_ajax:
                        return JsonResponse({'status': 'success', 'message': msg})
                    messages.success(request, msg)
                    return redirect(f'/admin/pnr-lookup/?pnr={pnr_code}')

                elif action in ['update_status', 'status_update']:
                    booking_id = request.POST.get('booking_id')
                    new_status_raw = request.POST.get('status', '').strip()
                    status_map = {
                        'pending': 'Pending',
                        'confirmed': 'Confirmed',
                        'checked_in': 'Checked-in',
                        'checkin': 'Checked-in',
                        'examining': 'Examining',
                        'completed': 'Completed',
                        'complete': 'Completed',
                        'cancelled': 'Cancelled',
                        'cancel': 'Cancelled',
                    }
                    target_status = status_map.get(new_status_raw.lower(), new_status_raw.capitalize() if new_status_raw else 'Pending')
                    
                    try:
                        b = Booking.objects.get(booking_id=booking_id)
                    except Booking.DoesNotExist:
                        if is_ajax:
                            return JsonResponse({'status': 'error', 'message': 'Không tìm thấy thông tin đặt lịch.'}, status=404)
                        messages.error(request, 'Không tìm thấy thông tin đặt lịch.')
                        return redirect(f'/admin/pnr-lookup/?pnr={pnr_code}')

                    old_status = b.status
                    b.status = target_status
                    b.save(update_fields=['status'])
                    BookingStatusHistory.objects.create(
                        booking=b,
                        status=target_status,
                        note=f'Đổi từ {old_status} sang {target_status} qua PNR Lookup'
                    )

                    msg = f'Đã đổi trạng thái khách #{b.booking_id} thành {target_status}'
                    if is_ajax:
                        return JsonResponse({'status': 'success', 'message': msg})
                    messages.success(request, msg)
                    return redirect(f'/admin/pnr-lookup/?pnr={pnr_code}')

                else:
                    if is_ajax:
                        return JsonResponse({'status': 'error', 'message': 'Hành động không hợp lệ.'}, status=400)
                    messages.error(request, 'Hành động không hợp lệ.')
                    return redirect(f'/admin/pnr-lookup/?pnr={pnr_code}')

        except Exception as e:
            if is_ajax:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            messages.error(request, f'Đã xảy ra lỗi: {str(e)}')
            return redirect(f'/admin/pnr-lookup/?pnr={pnr_code}')

    recent_pnrs = list(
        Booking.objects.exclude(pnr_code__isnull=True)
        .exclude(pnr_code__exact='')
        .order_by('-booking_id')
        .values_list('pnr_code', flat=True)
        .distinct()[:5]
    )

    context = {
        **admin.site.each_context(request),
        'title': 'Tra Cứu & Quản Trị PNR Nhóm Khách',
        'pnr_code': pnr_code.upper(),
        'recent_pnrs': recent_pnrs,
    }

    if pnr_code:
        bookings = Booking.objects.filter(
            Q(pnr_code__iexact=pnr_code) | Q(group_code__iexact=pnr_code)
        ).select_related(
            'customer', 'clinic', 'category', 'billing'
        ).prefetch_related(
            'details__service_detail', 'billing__payments'
        ).order_by('booking_id')

        if bookings.exists():
            total_amount = sum((b.total_amount for b in bookings), Decimal('0'))
            total_paid = sum((b.total_paid for b in bookings), Decimal('0'))
            remaining_balance = sum((b.remaining_balance for b in bookings), Decimal('0'))
            
            percent_paid = 0
            if total_amount > 0:
                percent_paid = int((total_paid / total_amount) * 100)

            first_booking = bookings.first()
            payment_status = 'PAID' if remaining_balance <= 0 and total_amount > 0 else ('PARTIAL' if total_paid > 0 else 'UNPAID')
            group_status = 'COMPLETED' if all(b.status in ['Completed', 'Cancelled', 'Đã xong', 'Đã hủy'] for b in bookings) else 'IN_PROGRESS'

            context['pnr_data'] = {
                'pnr_code': pnr_code.upper(),
                'clinic': first_booking.clinic if first_booking else None,
                'created_on': first_booking.created_on if first_booking else None,
                'total_passengers': bookings.count(),
                'bookings': bookings,
                'total_amount': total_amount,
                'total_paid': total_paid,
                'remaining_balance': remaining_balance,
                'percent_paid': percent_paid,
                'payment_status': payment_status,
                'group_status': group_status,
            }
        else:
            context['error'] = f'Không tìm thấy dữ liệu cho mã PNR \'{pnr_code}\''

    return render(request, 'admin/pnr_lookup.html', context)