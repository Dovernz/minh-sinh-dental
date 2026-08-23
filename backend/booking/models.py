from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models import Sum

class Clinic(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên chi nhánh")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    hotline = models.CharField(max_length=12, blank=True, null=True, verbose_name="Hotline")
    map_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Link Google Map")
    total_chairs = models.IntegerField(default=5, verbose_name="Tổng số ghế")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_clinic'

    def __str__(self):
        return self.name

class Service(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên dịch vụ")
    category = models.CharField(max_length=50, blank=True, null=True, verbose_name="Phân loại")
    duration_minutes = models.IntegerField(default=30, verbose_name="Thời gian (phút)")
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Giá dịch vụ')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_services'

    def __str__(self):
        return self.name

class TimeSlot(models.Model):
    start_time = models.TimeField(verbose_name="Thời gian bắt đầu")
    end_time = models.TimeField(verbose_name="Thời gian kết thúc")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_time_slots'

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class Customer(models.Model):
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    phone = models.CharField(max_length=12, unique=True, verbose_name="Số điện thoại")
    dob = models.DateField(blank=True, null=True, verbose_name="Ngày sinh")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Email")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_customers'

    def __str__(self):
        return self.full_name

class Employee(models.Model):
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Doctor', 'Doctor'),
        ('Reception', 'Reception'),
        ('Marketing', 'Marketing'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile', blank=True, null=True)
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    email = models.EmailField(max_length=50, blank=True, null=True, verbose_name="Email")
    specialty = models.CharField(max_length=50, blank=True, null=True, verbose_name="Chuyên môn")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Doctor', verbose_name="Vai trò")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_employees'

    def __str__(self):
        return self.full_name

class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    doctor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='handled_bookings', verbose_name='Bác sĩ khám')
    booking_date = models.DateField(verbose_name="Ngày khám", db_index=True)
    start_time = models.TimeField(verbose_name="Bắt đầu", db_index=True)
    end_time = models.TimeField(verbose_name="Kết thúc")
    chair_number = models.IntegerField(blank=True, null=True, verbose_name="Số ghế")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_bookings'

    def __str__(self):
        return f"{self.customer.full_name} - {self.booking_date} {self.start_time}"

class BookingStatus(models.Model):
    STATUS_CHOICES = [
        ('booked', 'booked'),
        ('paid', 'paid'),
        ('cancelled', 'cancelled'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='booked')
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_booking_status'

    def __str__(self):
        return f"{self.booking.id} - {self.status}"

class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('QR Code', 'QR Code'),
        ('Cash', 'Cash'),
        ('Card', 'Card'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Số tiền")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='QR Code', verbose_name="Phương thức")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_payments'

    def __str__(self):
        return f"{self.booking.id} - {self.amount}"

class InventoryDetail(models.Model):
    item_name = models.CharField(max_length=255, verbose_name="Tên vật tư")
    unit = models.CharField(max_length=50, verbose_name="Đơn vị tính")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="Phân loại")
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Giá vốn")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_inventory_details'

    def __str__(self):
        return self.item_name

class InventoryUsage(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='inventory_usages')
    item = models.ForeignKey(InventoryDetail, on_delete=models.RESTRICT, related_name='usages')
    quantity_used = models.PositiveIntegerField(verbose_name="Số lượng dùng")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người xuất/sử dụng")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_inventory_usage'

from ckeditor_uploader.fields import RichTextUploadingField

class Article(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Bản nháp'),
        ('Published', 'Xuất bản')
    ]
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    slug = models.SlugField(max_length=255, unique=True)
    content = RichTextUploadingField(verbose_name="Nội dung")
    thumbnail_url = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft', verbose_name="Trạng thái")
    word_file = models.FileField(upload_to='temp/', null=True, blank=True, verbose_name="Tải lên File Word (.docx)")
    
    # SEO fields
    meta_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="SEO Title")
    meta_description = models.TextField(blank=True, null=True, verbose_name="SEO Description")
    focus_keyword = models.CharField(max_length=255, blank=True, null=True, verbose_name="Focus Keyword")
    
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_articles'

    def __str__(self):
        return self.title



class TopupInfo(models.Model):
    bank_name = models.CharField(max_length=50, verbose_name='Tên ngân hàng (Mã)')
    account_number = models.CharField(max_length=50, verbose_name='Số tài khoản')
    account_name = models.CharField(max_length=100, verbose_name='Tên tài khoản')
    is_default = models.BooleanField(default=False, verbose_name='Mặc định')

    class Meta:
        db_table = 'db_table_topup_info'
        verbose_name = 'Cấu hình Thanh toán'
        verbose_name_plural = 'Cấu hình Thanh toán'

    def save(self, *args, **kwargs):
        if self.is_default:
            TopupInfo.objects.filter(is_default=True).update(is_default=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.bank_name} - {self.account_number}'
