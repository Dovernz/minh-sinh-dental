from django.contrib import admin
from .models import (
    Clinic, Service, TimeSlot, Customer, Employee, 
    Booking, BookingStatus, BookingBill, 
    InventoryDetail, InventoryUsage, Article
)

@admin.register(Clinic)
class ClinicAdmin(admin.ModelAdmin):
    list_display = ('name', 'hotline', 'created_on')
    search_fields = ('name', 'hotline', 'address')
    list_filter = ('created_on',)

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'duration_minutes', 'created_on')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'created_on')

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'dob', 'email', 'created_on')
    search_fields = ('full_name', 'phone', 'email')
    list_filter = ('created_on',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone', 'specialty', 'created_on')
    list_filter = ('specialty',)
    search_fields = ('full_name', 'phone', 'email')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('customer', 'clinic', 'service', 'employee', 'booking_date', 'start_time', 'status')
    list_filter = ('status', 'booking_date', 'clinic', 'service')
    search_fields = ('customer__full_name', 'customer__phone', 'employee__full_name', 'notes')
    date_hierarchy = 'booking_date'

@admin.register(BookingStatus)
class BookingStatusAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'changed_by', 'created_on')
    list_filter = ('status', 'created_on')
    search_fields = ('booking__customer__full_name',)

@admin.register(BookingBill)
class BookingBillAdmin(admin.ModelAdmin):
    list_display = ('booking', 'payment_amount', 'payment_method', 'customer_rating', 'created_on')
    list_filter = ('payment_method', 'customer_rating', 'created_on')
    search_fields = ('booking__customer__full_name',)

@admin.register(InventoryDetail)
class InventoryDetailAdmin(admin.ModelAdmin):
    list_display = ('item_name', 'unit', 'category', 'price_per_unit')
    list_filter = ('category',)
    search_fields = ('item_name',)

@admin.register(InventoryUsage)
class InventoryUsageAdmin(admin.ModelAdmin):
    list_display = ('booking', 'item', 'quantity_used', 'employee', 'created_on')
    list_filter = ('created_on',)
    search_fields = ('booking__customer__full_name', 'item__item_name', 'employee__full_name')

# Đăng ký luôn Article ở đây vì mô hình Article đang nằm trong app booking
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'user', 'created_on')
    search_fields = ('title', 'slug')
    list_filter = ('created_on',)
    prepopulated_fields = {'slug': ('title',)} # Tự động điền slug dựa trên title
