from django.utils import timezone
from datetime import timedelta, datetime, date
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from .models import ManageBooking
from booking.models import BookingStatusHistory, Payment

def is_staff(request):
    return request.user.groups.filter(name='Staff').exists() and not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists()

from django.contrib.admin import SimpleListFilter
from django.shortcuts import redirect, render
from booking.models import TimeSlot, Booking, Clinic
from .models import ManageBooking, DailySchedule, WeeklySchedule

class BaseRBACAdmin(ModelAdmin):
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

class BookingStatusHistoryInline(TabularInline):
    model = BookingStatusHistory
    extra = 1
    # Nhân viên chỉ có thể thêm, không thể sửa trạng thái cũ để đảm bảo tính lịch sử
    def has_change_permission(self, request, obj=None):
        return False

class PaymentInline(TabularInline):
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
    list_display = ('booking_id', 'get_customer_info', 'clinic', 'start_time', 'status')
    list_editable = ()
    list_filter = ('start_time', 'clinic', 'status')
    search_fields = ('customer__name', 'customer__phone', 'notes')
    date_hierarchy = 'start_time'
    inlines = [BookingStatusHistoryInline, PaymentInline]

    class Media:
        js = ('admin/js/booking_chained_select.js',)

    @admin.display(description='Kh?ch h?ng')
    def get_customer_info(self, obj):
        if obj.customer:
            name = getattr(obj.customer, 'name', getattr(obj.customer, 'full_name', ''))
            phone = getattr(obj.customer, 'phone', '')
            if name and phone:
                return f"{name} - {phone}"
            elif name:
                return name
            return phone
        return "-"

from django.utils.dateparse import parse_date

@admin.register(DailySchedule)
class DailyScheduleAdmin(BaseRBACAdmin):
    change_list_template = 'admin/operations/dailyschedule/change_list.html'

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser: return True
        return request.user.groups.filter(name__in=['Reception', 'Doctor']).exists()

    def changelist_view(self, request, extra_context=None):
        clinic_id_str = request.GET.get('custom_clinic')
        date_str = request.GET.get('custom_date')
        
        request.GET = request.GET.copy()
        request.GET.pop('custom_clinic', None)
        request.GET.pop('custom_date', None)

        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            import datetime
            from django.utils.dateparse import parse_date
            qs = response.context_data['cl'].queryset
            
            clinics = Clinic.objects.all()

            clinic_id = None
            if clinic_id_str:
                try:
                    clinic_id = int(clinic_id_str)
                except ValueError:
                    clinic_id = None
                    
            if not clinic_id:
                first_clinic = clinics.first()
                clinic_id = first_clinic.clinic_id if first_clinic else None
                
            selected_date = datetime.date.today()
            if date_str:
                try:
                    parsed_date = parse_date(date_str)
                    if parsed_date:
                        selected_date = parsed_date
                except ValueError:
                    pass
            
            # apply custom filters manually
            if clinic_id_str:
                qs = qs.filter(clinic_id=clinic_id)
            if date_str:
                qs = qs.filter(start_time__date=selected_date)
            elif not clinic_id_str and not date_str:
                qs = qs.filter(clinic_id=clinic_id, start_time__date=selected_date)
                
            qs = qs.exclude(status__iexact='cancelled').select_related('customer')
            
            clinic = clinics.filter(clinic_id=clinic_id).first()
            total_chairs = clinic.total_chairs if clinic else 5
            chairs = range(1, total_chairs + 1)
            
            time_slots = TimeSlot.objects.all().order_by('start_time')
            
            from django.utils.timezone import localtime
            booking_spans = []
            for b in qs:
                if not b.start_time or not b.end_time: continue
                b_start_local = localtime(b.start_time).time()
                b_end_local = localtime(b.end_time).time()
                booking_spans.append({"booking": b, "start": b_start_local, "end": b_end_local, "chair": None})
            
            matrix = []
            for ts in time_slots:
                row = {'time': f"{ts.start_time.strftime('%H:%M')} - {ts.end_time.strftime('%H:%M')}", 'chairs': {}}
                
                active_bookings = []
                for span in booking_spans:
                    if span["start"] < ts.end_time and span["end"] > ts.start_time:
                        active_bookings.append(span)
                        
                used_chairs = set(span["chair"] for span in active_bookings if span["chair"] is not None)
                for span in active_bookings:
                    if span["chair"] is None:
                        for c in chairs:
                            if c not in used_chairs:
                                span["chair"] = c
                                used_chairs.add(c)
                                break
                                
                for c in chairs:
                    active_span = next((s for s in active_bookings if s["chair"] == c), None)
                    row['chairs'][c] = active_span["booking"] if active_span else None
                
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
        clinic_id_str = request.GET.get('custom_clinic')
        start_date_str = request.GET.get('custom_start_date')
        end_date_str = request.GET.get('custom_end_date')
        
        request.GET = request.GET.copy()
        request.GET.pop('custom_clinic', None)
        request.GET.pop('custom_start_date', None)
        request.GET.pop('custom_end_date', None)

        response = super().changelist_view(request, extra_context)
        if hasattr(response, 'context_data') and 'cl' in response.context_data:
            from django.utils.dateparse import parse_date
            import datetime
            qs = response.context_data['cl'].queryset
            
            clinics = Clinic.objects.all()

            clinic_id = None
            if clinic_id_str:
                try:
                    clinic_id = int(clinic_id_str)
                except ValueError:
                    clinic_id = None

            if not clinic_id:
                first_clinic = clinics.first()
                clinic_id = first_clinic.clinic_id if first_clinic else None

            start_date = parse_date(start_date_str) if start_date_str else datetime.date.today()
            if not start_date:
                start_date = datetime.date.today()
            
            end_date = parse_date(end_date_str) if end_date_str else start_date + timedelta(days=6)
            if not end_date or end_date < start_date:
                end_date = start_date + timedelta(days=6)
            
            # apply custom filters manually
            if clinic_id_str:
                qs = qs.filter(clinic_id=clinic_id)
            if start_date_str or end_date_str:
                qs = qs.filter(start_time__date__gte=start_date, start_time__date__lte=end_date)
            elif not clinic_id_str and not start_date_str:
                qs = qs.filter(clinic_id=clinic_id, start_time__date__gte=start_date, start_time__date__lte=end_date)
                
            qs = qs.exclude(status__iexact='cancelled').distinct()
            
            time_slots = TimeSlot.objects.all().order_by('start_time')
            
            from django.utils.timezone import localtime
            counts_map = {}
            for b in qs:
                if b.start_time and b.end_time:
                    b_date = localtime(b.start_time).date()
                    b_start_local = localtime(b.start_time).time()
                    b_end_local = localtime(b.end_time).time()
                    
                    for ts in time_slots:
                        if b_start_local < ts.end_time and b_end_local > ts.start_time:
                            key = (b_date, ts.start_time)
                            counts_map[key] = counts_map.get(key, 0) + 1
            
            days = []
            current = start_date
            while current <= end_date:
                days.append(current)
                current += timedelta(days=1)
            
            clinic = clinics.filter(clinic_id=clinic_id).first()
            total_chairs = clinic.total_chairs if clinic else 5
            
            grid_data = []
            for ts in time_slots:
                row = {'time': f"{ts.start_time.strftime('%H:%M')} - {ts.end_time.strftime('%H:%M')}", 'days': []}
                for current_date in days:
                    booked_count = counts_map.get((current_date, ts.start_time), 0)
                    percent = (booked_count / total_chairs) * 100 if total_chairs > 0 else 0
                    
                    # 1. Trạng thái Đầy (Đỏ): Nền đỏ nhạt, chữ đỏ đậm (Giao diện sáng) | Nền đỏ/đen mờ, chữ đỏ nhạt (Giao diện tối)
                    if percent >= 100:
                        color_class = 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-400'

                    # 2. Trạng thái Gần đầy (Vàng):
                    elif percent >= 80:
                        color_class = 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-400'

                    # 3. Trạng thái Trống (Xanh) - ĐÃ LÀM DỊU MÀU:
                    else:
                        color_class = 'bg-green-100 text-green-800 dark:bg-white/30 dark:text-green-400'
                        
                    row['days'].append({
                        'booked': booked_count,
                        'total': total_chairs,
                        'color': color_class,
                    })
                grid_data.append(row)
                
            response.context_data['grid_data'] = grid_data
            response.context_data['days'] = days
            response.context_data['clinic'] = clinic
            response.context_data['clinics'] = clinics
            response.context_data['selected_start_date'] = start_date.strftime('%Y-%m-%d')
            response.context_data['selected_end_date'] = end_date.strftime('%Y-%m-%d')
            response.context_data['selected_clinic_id'] = str(clinic_id) if clinic_id else ''
            
        return response
