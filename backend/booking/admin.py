from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import (
    Clinic, Service, TimeSlot, Customer, Employee, 
    Booking, BookingStatus, Payment, TopupInfo,
    InventoryDetail, InventoryUsage, Article
)


admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Admin').exists()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Admin').exists()

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        new_fieldsets = []
        for name, opts in fieldsets:
            fields = list(opts.get('fields', []))
            if 'last_login' in fields: fields.remove('last_login')
            if 'date_joined' in fields: fields.remove('date_joined')
            
            # Chặn nhóm Admin tự ý cấp quyền is_superuser
            if not request.user.is_superuser and 'is_superuser' in fields:
                fields.remove('is_superuser')
                
            if fields:
                new_fieldsets.append((name, {**opts, 'fields': tuple(fields)}))
        return tuple(new_fieldsets)

def is_staff(request):
    return request.user.groups.filter(name='Staff').exists() and not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists()

class BaseRBACAdmin(admin.ModelAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False
        
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False

@admin.register(TopupInfo)
class TopupInfoAdmin(BaseRBACAdmin):
    list_display = ('bank_name', 'account_number', 'account_name', 'is_default')
    list_filter = ('is_default',)

@admin.register(Clinic)
class ClinicAdmin(BaseRBACAdmin):
    list_display = ('name', 'hotline', 'created_on')
    search_fields = ('name', 'hotline', 'address')
    list_filter = ('created_on',)

@admin.register(Service)
class ServiceAdmin(BaseRBACAdmin):
    list_display = ('name', 'category', 'duration_minutes', 'created_on')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(TimeSlot)
class TimeSlotAdmin(BaseRBACAdmin):
    list_display = ('start_time', 'end_time', 'created_on')

@admin.register(Customer)
class CustomerAdmin(BaseRBACAdmin):
    list_display = ('full_name', 'phone', 'dob', 'email', 'created_on')
    search_fields = ('full_name', 'phone', 'email')
    list_filter = ('created_on',)

@admin.register(Employee)
class EmployeeAdmin(BaseRBACAdmin):
    exclude = ('user',)
    list_display = ('full_name', 'phone', 'specialty', 'role', 'created_on')
    list_filter = ('specialty', 'role')
    search_fields = ('full_name', 'phone', 'email')

    def save_model(self, request, obj, form, change):
        if obj.role == 'Admin' and not request.user.is_superuser:
            raise PermissionDenied('Chỉ Superuser mới được tạo Admin')
            
        if not change:
            username = obj.phone or obj.email or f"user_{obj.id}"
            new_user = User.objects.create_user(username=username, password='password123')
            obj.user = new_user
            
        if obj.user and obj.role:
            group = Group.objects.get(name=obj.role)
            obj.user.groups.clear()
            obj.user.groups.add(group)
            obj.user.is_staff = True
            obj.user.save()
            
        super().save_model(request, obj, form, change)

@admin.register(Booking)
class BookingAdmin(BaseRBACAdmin):
    list_display = ('id', 'customer', 'doctor', 'service', 'booking_date', 'start_time')
    list_filter = ('booking_date', 'clinic', 'service', 'doctor')
    search_fields = ('customer__full_name', 'customer__phone', 'doctor__full_name', 'notes')
    date_hierarchy = 'booking_date'

@admin.register(BookingStatus)
class BookingStatusAdmin(BaseRBACAdmin):
    list_display = ('booking', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('booking__customer__full_name',)
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Payment)
class PaymentAdmin(BaseRBACAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'created_at')
    list_filter = ('payment_method', 'created_at')
    search_fields = ('booking__customer__full_name',)



@admin.register(InventoryDetail)
class InventoryDetailAdmin(BaseRBACAdmin):
    list_display = ('item_name', 'unit', 'category', 'price_per_unit')
    list_filter = ('category',)
    search_fields = ('item_name',)

@admin.register(InventoryUsage)
class InventoryUsageAdmin(BaseRBACAdmin):
    list_display = ('booking', 'item', 'quantity_used', 'employee', 'created_on')
    list_filter = ('created_on',)
    search_fields = ('booking__customer__full_name', 'item__item_name', 'employee__full_name')

@admin.register(Article)
class ArticleAdmin(BaseRBACAdmin):
    list_display = ('title', 'slug', 'user', 'created_on')
    search_fields = ('title', 'slug')
    list_filter = ('created_on',)
    prepopulated_fields = {'slug': ('title',)}
