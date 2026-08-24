from django.contrib import admin
from .models import ManageBooking
from booking.models import BookingStatus, Payment

def is_staff(request):
    return request.user.groups.filter(name='Staff').exists() and not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists()

from django.contrib.admin import SimpleListFilter
from django.shortcuts import redirect, render
from datetime import date, timedelta
from booking.models import TimeSlot, Booking, Clinic
from .models import ManageBooking, DailySchedule, WeeklySchedule

class BaseRBACAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name__in=['Reception', 'Doctor']).exists()

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name__in=['Reception', 'Doctor', 'Admin']).exists()

    def has_add_permission(self, request):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name__in=['Reception', 'Admin']).exists()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name__in=['Reception', 'Admin']).exists()
        
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name__in=['Reception', 'Admin']).exists()

class BookingStatusInline(admin.TabularInline):
    model = BookingStatus
    extra = 1
    # Nhân viên chỉ có thể thêm, không thể sửa trạng thái cũ để đảm bảo tính lịch sử
    def has_change_permission(self, request, obj=None):
        return False

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 1

from django.utils.html import format_html
from django.urls import path
from django.http import JsonResponse
from django.db import transaction
import json
from django.views.decorators.csrf import csrf_exempt

@admin.register(ManageBooking)
class ManageBookingAdmin(BaseRBACAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name='Reception').exists()
        
    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name='Reception').exists()
        
    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name='Reception').exists()

    from booking.admin import BookingAdminForm
    form = BookingAdminForm
    list_display = ('booking_id', 'customer', 'category', 'current_status', 'total_paid', 'quick_payment_ui')
    list_editable = ()
    list_filter = ('booking_date', 'clinic', 'category')
    # readonly_fields = ('category',) # Bỏ để kích hoạt AJAX
    search_fields = ('customer__full_name', 'customer__phone', 'doctor__full_name', 'notes')
    date_hierarchy = 'booking_date'
    inlines = [BookingStatusInline, PaymentInline]

    class Media:
        js = ('admin/js/quick_pay.js', 'admin/js/booking_chained_select.js')

    def save_model(self, request, obj, form, change):
        if not obj.actual_price and obj.service_detail:
            obj.actual_price = obj.service_detail.price
        super().save_model(request, obj, form, change)

    @admin.display(description='Thanh toán nhanh')
    def quick_payment_ui(self, obj):
        return format_html(
            '''
            <div style="display: flex; gap: 5px; align-items: center;">
                <input type="number" class="quick-amount" id="quick-pay-amount-{0}" placeholder="Nhập số tiền" style="width: 100px; padding: 2px;">
                <select class="quick-method" id="quick-pay-method-{0}" style="padding: 2px;">
                    <option value="Cash">Cash</option>
                    <option value="Card">Card</option>
                    <option value="QR Code">QR Code</option>
                </select>
                <button type="button" class="button quick-pay-btn" data-booking-id="{0}" onclick="handleQuickPay({0})" style="margin:0;">Xác nhận</button>
            </div>
            ''',
            obj.booking_id
        )

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('quick-pay/', self.admin_site.admin_view(self.quick_pay_view), name='operations_managebooking_quick_pay'),
            path('bank-config/', self.admin_site.admin_view(self.bank_config_view), name='operations_managebooking_bank_config'),
        ]
        return custom_urls + urls
        
    def bank_config_view(self, request):
        from booking.models import TopupInfo
        try:
            default_bank = TopupInfo.objects.filter(is_default=True).first()
            if default_bank:
                return JsonResponse({
                    'status': 'success', 
                    'bank_name': default_bank.bank_name, 
                    'account_number': default_bank.account_number, 
                    'account_name': default_bank.account_name
                })
            return JsonResponse({'status': 'error', 'message': 'Chưa cấu hình ngân hàng mặc định'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    def quick_pay_view(self, request):
        if request.method == 'POST':
            try:
                data = json.loads(request.body)
                booking_id = data.get('booking_id')
                amount = data.get('amount')
                method = data.get('method')

                if not booking_id or not amount or not method:
                    return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin'}, status=400)

                with transaction.atomic():
                    booking = ManageBooking.objects.get(pk=booking_id)
                    Payment.objects.create(
                        booking=booking,
                        amount=amount,
                        payment_method=method
                    )
                    BookingStatus.objects.create(
                        booking=booking,
                        status='paid',
                        note='Thanh toán nhanh qua Admin'
                    )
                return JsonResponse({'status': 'success'})
            except Exception as e:
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

from django.utils.dateparse import parse_date

@admin.register(DailySchedule)
class DailyScheduleAdmin(BaseRBACAdmin):
    change_list_template = 'admin/operations/dailyschedule/change_list.html'

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name__in=['Reception', 'Doctor']).exists()

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            import datetime
            qs = response.context_data['cl'].queryset
            
            clinics = Clinic.objects.all()
            clinic_id = request.GET.get('clinic_id')
            date_str = request.GET.get('booking_date')

            if not clinic_id:
                first_clinic = clinics.first()
                clinic_id = str(first_clinic.clinic_id) if first_clinic else None
                
            try:
                selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else datetime.date.today()
            except ValueError:
                selected_date = datetime.date.today()
            
            # Đảm bảo qs luôn được filter theo clinic_id và booking_date nếu thiếu trên URL
            if not request.GET.get('clinic_id'):
                qs = qs.filter(clinic_id=clinic_id)
            if not request.GET.get('booking_date'):
                qs = qs.filter(booking_date=selected_date)
                
            qs = qs.exclude(status_history__status__iexact='cancelled').select_related('customer', 'service')
            
            clinic = clinics.filter(id=clinic_id).first()
            total_chairs = clinic.total_chairs if clinic else 5
            chairs = range(1, total_chairs + 1)
            
            time_slots = TimeSlot.objects.all().order_by('start_time')
            
            matrix = []
            for ts in time_slots:
                row = {'time': f"{ts.start_time.strftime('%H:%M')} - {ts.end_time.strftime('%H:%M')}", 'chairs': {}}
                ts_bookings = qs.filter(start_time=ts.start_time)
                for c in chairs:
                    b = ts_bookings.filter(chair_number=c).first()
                    row['chairs'][c] = b
                matrix.append(row)
                
            response.context_data['matrix'] = matrix
            response.context_data['chairs'] = chairs
            response.context_data['clinic'] = clinic
            response.context_data['clinics'] = clinics
            response.context_data['selected_start_date'] = selected_date.strftime('%Y-%m-%d')
            response.context_data['selected_clinic_id'] = str(clinic_id) if clinic_id else ''
            
        return response

@admin.register(WeeklySchedule)
class WeeklyScheduleAdmin(BaseRBACAdmin):
    change_list_template = 'admin/operations/weeklyschedule/change_list.html'

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name__in=['Reception', 'Doctor']).exists()

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            qs = response.context_data['cl'].queryset
            
            clinics = Clinic.objects.all()
            clinic_id = request.GET.get('clinic_id')
            start_date_str = request.GET.get('booking_date__gte')
            end_date_str = request.GET.get('booking_date__lte')

            if not clinic_id:
                first_clinic = clinics.first()
                clinic_id = str(first_clinic.clinic_id) if first_clinic else None

            start_date = parse_date(start_date_str) if start_date_str else date.today()
            if not start_date:
                start_date = date.today()
            
            end_date = parse_date(end_date_str) if end_date_str else start_date + timedelta(days=6)
            if not end_date or end_date < start_date:
                end_date = start_date + timedelta(days=6)
            
            # Đảm bảo qs được filter nếu thiếu param trên URL
            if not request.GET.get('clinic_id'):
                qs = qs.filter(clinic_id=clinic_id)
            if not request.GET.get('booking_date__gte') or not request.GET.get('booking_date__lte'):
                qs = qs.filter(booking_date__gte=start_date, booking_date__lte=end_date)
                
            qs = qs.exclude(status_history__status__iexact='cancelled').distinct()
            
            # Tối ưu hóa Database: Đẩy việc đếm tổng (Aggregation) cho cơ sở dữ liệu
            # Dùng order_by() để xóa các ordering mặc định, đảm bảo GROUP BY đúng
            from django.db.models import Count
            aggregated_data = qs.order_by().values('booking_date', 'start_time').annotate(total_bookings=Count('id'))
            counts_map = {}
            for item in aggregated_data:
                counts_map[(item['booking_date'], item['start_time'])] = item['total_bookings']
            
            days = []
            current = start_date
            while current <= end_date:
                days.append(current)
                current += timedelta(days=1)
            
            clinic = clinics.filter(id=clinic_id).first()
            total_chairs = clinic.total_chairs if clinic else 5
            
            time_slots = TimeSlot.objects.all().order_by('start_time')
            
            matrix = []
            for ts in time_slots:
                row = {'time': f"{ts.start_time.strftime('%H:%M')} - {ts.end_time.strftime('%H:%M')}", 'days': []}
                for d in days:
                    count = counts_map.get((d, ts.start_time), 0)
                    occupancy = (count / total_chairs) * 100 if total_chairs > 0 else 0
                    if occupancy < 80:
                        color = 'green'
                    elif occupancy < 100:
                        color = 'orange'
                    else:
                        color = 'red'
                    
                    row['days'].append({
                        'date': d,
                        'count': count,
                        'total': total_chairs,
                        'color': color
                    })
                matrix.append(row)
                
            response.context_data['matrix'] = matrix
            response.context_data['days'] = days
            response.context_data['clinic'] = clinic
            response.context_data['clinics'] = clinics
            response.context_data['selected_start_date'] = start_date.strftime('%Y-%m-%d')
            response.context_data['selected_end_date'] = end_date.strftime('%Y-%m-%d')
            response.context_data['selected_clinic_id'] = str(clinic_id) if clinic_id else ''
            
        return response
