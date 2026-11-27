import threading
from datetime import datetime as dt_module, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Clinic, TimeSlot, Booking, Customer, ServiceCategory, BookingStatusHistory
from .pnr_utils import generate_pnr_code
from .schedule_services import (
    INACTIVE_BOOKING_STATUSES,
    get_clinic_total_chairs,
    get_slot_capacity,
    get_valid_time_slots_from,
    make_aware_dt,
    compute_auto_distribution,
)


class AvailableSlotsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        clinic_id = request.query_params.get('clinic_id')
        date_str = request.query_params.get('date') or request.query_params.get('appointment_date')

        if not clinic_id or not date_str:
            return Response(
                {'error': 'Thiếu tham số clinic_id hoặc date.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy phòng khám.'},
                status=status.HTTP_404_NOT_FOUND
            )

        target_date = parse_date(date_str)
        if not target_date:
            return Response(
                {'error': 'Định dạng ngày không hợp lệ (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        time_slots = TimeSlot.objects.all().order_by('start_time')
        if not time_slots.exists():
            time_slots = get_valid_time_slots_from(dt_module.strptime('08:00', '%H:%M').time())

        day_start = make_aware_dt(target_date, dt_module.min.time())
        day_end = day_start + timedelta(days=1)

        bookings = Booking.objects.filter(
            clinic=clinic,
            start_time__gte=day_start,
            start_time__lt=day_end
        ).exclude(status__in=INACTIVE_BOOKING_STATUSES)

        total_chairs = get_clinic_total_chairs(clinic)
        results = []

        now_local = timezone.localtime(timezone.now())
        today_local = now_local.date()

        for ts in time_slots:
            slot_start_dt = make_aware_dt(target_date, ts.start_time)
            slot_end_dt = make_aware_dt(target_date, ts.end_time)

            booked_count = sum(
                1 for b in bookings
                if b.start_time and (
                    b_start := b.start_time,
                    b_end := b.end_time or (b.start_time + timedelta(minutes=b.estimated_duration or 30)),
                    b_start < slot_end_dt and b_end > slot_start_dt
                )[-1]
            )

            available = max(0, total_chairs - booked_count)
            is_full = available <= 0
            is_past = (target_date < today_local) or (slot_start_dt <= now_local)
            is_available = (not is_full) and (not is_past)
            slot_status = 'past' if is_past else ('full' if is_full else 'available')

            if is_past:
                warning_message = f"Khung giờ {ts.start_time.strftime('%H:%M')} đã qua."
            elif is_full:
                warning_message = f"Khung giờ {ts.start_time.strftime('%H:%M')} đã hết ghế trống."
            else:
                warning_message = None

            results.append({
                'time': f"{ts.start_time.strftime('%H:%M')} - {ts.end_time.strftime('%H:%M')}",
                'start_time': ts.start_time.strftime('%H:%M'),
                'end_time': ts.end_time.strftime('%H:%M'),
                'available_chairs': available,
                'total_chairs': total_chairs,
                'max_chairs': total_chairs,
                'booked_count': booked_count,
                'occupied_chairs': booked_count,
                'active_bookings': booked_count,
                'is_full': is_full,
                'is_past': is_past,
                'is_available': is_available,
                'status': slot_status,
                'warning_message': warning_message
            })

        return Response(results, status=status.HTTP_200_OK)


class BookingDistributionPreviewView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def _handle(self, data):
        clinic_id = data.get('clinic_id')
        date_str = data.get('date') or data.get('appointment_date')
        start_time_str = data.get('start_time') or data.get('leader_start_time')
        patients = data.get('patients')
        passenger_count = data.get('passenger_count')
        duration = int(data.get('duration') or 30)

        if not clinic_id or not date_str or not start_time_str:
            return Response(
                {'error': 'Thiếu tham số bắt buộc (clinic_id, date, start_time).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy phòng khám.'},
                status=status.HTTP_404_NOT_FOUND
            )

        target_date = parse_date(date_str)
        if not target_date:
            return Response(
                {'error': 'Định dạng ngày không hợp lệ (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            req_start_time = dt_module.strptime(start_time_str, '%H:%M').time()
        except ValueError:
            return Response(
                {'error': 'Định dạng giờ không hợp lệ (HH:MM).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if isinstance(patients, list) and len(patients) > 0:
            normalized_patients = []
            for idx, p in enumerate(patients):
                guest_order = int(p.get('guest_order') or p.get('passenger_index') or p.get('guest_index') or (idx + 1))
                guest_label = p.get('guest_label') or f'Khách {guest_order}'
                normalized_patients.append({
                    'guest_order': guest_order,
                    'guest_label': guest_label,
                    'fullName': p.get('fullName') or p.get('full_name') or p.get('name') or guest_label,
                    'phone': p.get('phone'),
                    'category_id': p.get('category_id'),
                    'service_name': p.get('service_name'),
                    'duration': int(p.get('duration') or duration),
                    'start_time': p.get('start_time') or p.get('time')
                })
        else:
            try:
                p_count = int(passenger_count or 1)
            except (ValueError, TypeError):
                p_count = 1
            normalized_patients = []
            for i in range(max(1, p_count)):
                guest_order = i + 1
                guest_label = f'Khách {guest_order}'
                normalized_patients.append({
                    'guest_order': guest_order,
                    'guest_label': guest_label,
                    'fullName': guest_label,
                    'duration': duration
                })

        dist = compute_auto_distribution(
            clinic, target_date, req_start_time, normalized_patients, default_duration=duration
        )

        if 'distributed_patients' in dist:
            for item in dist['distributed_patients']:
                item.pop('assigned_start_dt', None)
                item.pop('assigned_end_dt', None)
                guest_order = item.get('guest_order', 1)
                guest_label = item.get('guest_label', f'Khách {guest_order}')
                item.setdefault('guest_order', guest_order)
                item.setdefault('guest_label', guest_label)
                item.setdefault('name', item.get('fullName') or item.get('full_name') or guest_label)
                item.setdefault('assigned_time', item.get('assigned_start_time'))

        if 'distribution_summary' in dist:
            for summary in dist['distribution_summary']:
                summary.setdefault('count', summary.get('assigned_count', 0))

        return Response(dist, status=status.HTTP_200_OK)

    def post(self, request):
        return self._handle(request.data)

    def get(self, request):
        return self._handle(request.query_params)


class BookingCreateView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        clinic_id = data.get('clinic_id')
        date_str = data.get('date') or data.get('appointment_date')
        default_start_time_str = data.get('start_time') or data.get('leader_start_time')
        patients = data.get('patients', [])
        created_user_id = data.get('created_user_id')
        
        auto_distribute = data.get('auto_distribute', True)
        if isinstance(auto_distribute, str):
            auto_distribute = auto_distribute.lower() not in ('false', '0', 'no')

        if not patients and (data.get('passenger_count') or data.get('leader_name') or data.get('fullName')):
            p_count = int(data.get('passenger_count') or 1)
            leader_name = data.get('leader_name') or data.get('fullName') or 'Khách hàng'
            leader_phone = data.get('leader_phone') or data.get('phone') or ''
            patients = []
            for i in range(p_count):
                guest_order = i + 1
                guest_label = f'Khách {guest_order}'
                patients.append({
                    'guest_order': guest_order,
                    'guest_label': guest_label,
                    'fullName': leader_name if i == 0 else f"{leader_name} - {guest_label}",
                    'phone': leader_phone,
                    'start_time': default_start_time_str,
                    'category_id': data.get('category_id')
                })

        if not clinic_id or not date_str or not patients:
            return Response(
                {'error': 'Thiếu thông tin bắt buộc (clinic_id, date, patients).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy phòng khám.'},
                status=status.HTTP_404_NOT_FOUND
            )

        target_date = parse_date(date_str)
        if not target_date:
            return Response(
                {'error': 'Định dạng ngày không hợp lệ (YYYY-MM-DD).'},
                status=status.HTTP_400_BAD_REQUEST
            )

        prepared_patients = []
        for idx, p in enumerate(patients):
            guest_order = int(p.get('guest_order') or p.get('passenger_index') or p.get('guest_index') or (idx + 1))
            guest_label = p.get('guest_label') or f'Khách {guest_order}'

            name = p.get('fullName') or p.get('full_name') or guest_label
            phone = p.get('phone')
            if not name or not phone:
                return Response(
                    {'error': 'Mỗi khách hàng phải có fullName và phone.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            p_time_str = p.get('start_time') or p.get('time') or default_start_time_str
            if not p_time_str:
                return Response(
                    {'error': 'Thiếu thời gian bắt đầu cho lịch hẹn.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                p_time = dt_module.strptime(p_time_str, '%H:%M').time()
            except ValueError:
                return Response(
                    {'error': f'Định dạng giờ không hợp lệ: {p_time_str}'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            cat_id = p.get('category_id') or data.get('category_id')
            p_category = None
            p_duration = 30
            if cat_id:
                try:
                    p_category = ServiceCategory.objects.get(pk=cat_id)
                    if p_category.estimate_time:
                        p_duration = p_category.estimate_time
                except ServiceCategory.DoesNotExist:
                    pass

            raw_note = p.get('note', '')
            if raw_note:
                if guest_label not in raw_note:
                    formatted_note = f"[Khách {guest_order}] {raw_note}"
                else:
                    formatted_note = raw_note
            else:
                formatted_note = guest_label

            prepared_patients.append({
                'guest_order': guest_order,
                'guest_label': guest_label,
                'fullName': name,
                'full_name': name,
                'phone': phone,
                'start_time': p_time,
                'start_time_str': p_time_str,
                'category': p_category,
                'category_id': cat_id,
                'duration': int(p.get('duration') or p_duration),
                'note': formatted_note
            })

        primary_start_time = prepared_patients[0]['start_time']

        with transaction.atomic():
            locked_clinic = Clinic.objects.select_for_update().get(pk=clinic.pk)

            needs_distribution = False
            dist_warning = None
            dist_summary = None
            batch_allocated_slots = []

            if auto_distribute:
                all_fit_without_shift = True
                temp_allocated = []
                for p in prepared_patients:
                    p_start_dt = make_aware_dt(target_date, p['start_time'])
                    p_end_dt = p_start_dt + timedelta(minutes=p['duration'])
                    cap_info = get_slot_capacity(
                        locked_clinic, target_date, p['start_time'],
                        duration_minutes=p['duration'],
                        extra_occupied_spans=temp_allocated
                    )
                    if cap_info['available_chairs'] <= 0:
                        all_fit_without_shift = False
                        break
                    temp_allocated.append({'start': p_start_dt, 'end': p_end_dt})

                if all_fit_without_shift:
                    dist = {
                        'can_fulfill_all': True,
                        'distributed_patients': [
                            {
                                'guest_order': p['guest_order'],
                                'guest_label': p['guest_label'],
                                'fullName': p['fullName'],
                                'phone': p['phone'],
                                'category_id': p['category_id'],
                                'category': p['category'],
                                'duration': p['duration'],
                                'note': p['note'],
                                'assigned_start_dt': make_aware_dt(target_date, p['start_time']),
                                'assigned_end_dt': make_aware_dt(target_date, p['start_time']) + timedelta(minutes=p['duration']),
                                'start_time': p['start_time'].strftime('%H:%M')
                            }
                            for p in prepared_patients
                        ]
                    }
                    needs_distribution = False
                else:
                    dist = compute_auto_distribution(
                        locked_clinic, target_date, primary_start_time, prepared_patients, default_duration=30
                    )
                    needs_distribution = True

                if not dist.get('can_fulfill_all', True):
                    return Response({
                        'error': dist.get('warning_message', 'Không đủ ghế trống để xếp lịch.'),
                        'warning_message': dist.get('warning_message'),
                        'unassigned_count': dist.get('unassigned_count', 0),
                        'distribution_summary': dist.get('distribution_summary', {})
                    }, status=status.HTTP_400_BAD_REQUEST)

                dist_warning = dist.get('warning_message')
                dist_summary = dist.get('distribution_summary')
                final_distribution = dist['distributed_patients']

            else:
                final_distribution = []
                for p in prepared_patients:
                    p_start_dt = make_aware_dt(target_date, p['start_time'])
                    p_end_dt = p_start_dt + timedelta(minutes=p['duration'])
                    cap_info = get_slot_capacity(
                        locked_clinic, target_date, p['start_time'],
                        duration_minutes=p['duration'],
                        extra_occupied_spans=batch_allocated_slots
                    )
                    if cap_info['available_chairs'] <= 0:
                        suggested = compute_auto_distribution(
                            locked_clinic, target_date, primary_start_time, prepared_patients, default_duration=30
                        )
                        return Response({
                            'error': f"Khung giờ {p['start_time'].strftime('%H:%M')} đã hết ghế trống.",
                            'warning': f"Khung giờ {p['start_time'].strftime('%H:%M')} đã hết ghế trống.",
                            'warning_message': f"Khung giờ {p['start_time'].strftime('%H:%M')} đã hết ghế trống.",
                            'available_chairs': cap_info['available_chairs'],
                            'total_chairs': cap_info['total_chairs'],
                            'occupied_chairs': cap_info['occupied_chairs'],
                            'suggested_distribution': {
                                'distribution_summary': suggested.get('distribution_summary', []),
                                'warning_message': suggested.get('warning_message'),
                            }
                        }, status=status.HTTP_400_BAD_REQUEST)

                    batch_allocated_slots.append({'start': p_start_dt, 'end': p_end_dt})
                    final_distribution.append({
                        **p,
                        'assigned_start_dt': p_start_dt,
                        'assigned_end_dt': p_end_dt
                    })

            pnr_code = generate_pnr_code(prefix='MS')
            group_code = pnr_code
            created_booking_ids = []
            bookings_info = []

            for item in final_distribution:
                cust_name = item.get('fullName') or item.get('full_name')
                cust_phone = item.get('phone')
                customer, _ = Customer.objects.get_or_create(
                    phone=cust_phone,
                    defaults={'name': cust_name}
                )

                assigned_start = item['assigned_start_dt']
                assigned_end = item['assigned_end_dt']
                duration_val = item.get('duration', 30)
                g_order = int(item.get('guest_order', 1))
                g_label = item.get('guest_label', f'Khách {g_order}')
                item_note = item.get('note', '')

                booking = Booking.objects.create(
                    clinic=locked_clinic,
                    customer=customer,
                    category=item.get('category'),
                    start_time=assigned_start,
                    end_time=assigned_end,
                    estimated_duration=duration_val,
                    status='Pending',
                    pnr_code=pnr_code,
                    group_code=group_code,
                    created_user_id=created_user_id,
                    notes=item_note,
                    guest_order=g_order
                )

                BookingStatusHistory.objects.create(
                    booking=booking,
                    status='Pending',
                    note='Đặt lịch từ website'
                )

                created_booking_ids.append(booking.booking_id)
                bookings_info.append({
                    'booking_id': booking.booking_id,
                    'pnr_code': pnr_code,
                    'guest_order': g_order,
                    'guest_label': g_label,
                    'customer_name': cust_name,
                    'customer_phone': cust_phone,
                    'start_time': timezone.localtime(assigned_start).strftime('%H:%M'),
                    'end_time': timezone.localtime(assigned_end).strftime('%H:%M'),
                    'notes': item_note,
                    'is_shifted': item.get('is_shifted', False),
                    'status': booking.status
                })

        def send_async_emails():
            try:
                for info in bookings_info:
                    send_mail(
                        subject=f"Xác nhận đặt lịch khám - PNR: {info['pnr_code']}",
                        message=f"Chào {info['customer_name']},\n\nLịch hẹn của bạn tại phòng khám đã được xác nhận vào lúc {info['start_time']}.\nMã PNR của bạn là: {info['pnr_code']}\n\nXin cảm ơn!",
                        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@dental.com'),
                        recipient_list=[prepared_patients[0]['phone']] if '@' in prepared_patients[0].get('phone', '') else [],
                        fail_silently=True,
                    )
            except Exception:
                pass

        threading.Thread(target=send_async_emails, daemon=True).start()

        total_chairs = get_clinic_total_chairs(locked_clinic)

        return JsonResponse({
            'pnr_code': pnr_code,
            'group_code': group_code,
            'created_booking_ids': created_booking_ids,
            'booking_id': created_booking_ids[0] if created_booking_ids else None,
            'status': 'success',
            'auto_distributed': needs_distribution,
            'needs_distribution': needs_distribution,
            'total_chairs': total_chairs,
            'warning_message': dist_warning,
            'distribution_summary': dist_summary,
            'bookings': bookings_info,
            'message': f"Đặt lịch thành công cho {len(created_booking_ids)} khách hàng! Mã PNR: {pnr_code}"
        }, status=201)