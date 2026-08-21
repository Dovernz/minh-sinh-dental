from django.db import models
from django.contrib.auth.models import User

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
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile', blank=True, null=True)
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    email = models.EmailField(max_length=50, blank=True, null=True, verbose_name="Email")
    specialty = models.CharField(max_length=50, blank=True, null=True, verbose_name="Chuyên môn")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_employees'

    def __str__(self):
        return self.full_name

class Booking(models.Model):
    STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    booking_date = models.DateField(verbose_name="Ngày khám")
    start_time = models.TimeField(verbose_name="Bắt đầu")
    end_time = models.TimeField(verbose_name="Kết thúc")
    chair_number = models.IntegerField(blank=True, null=True, verbose_name="Số ghế")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Booked', verbose_name="Trạng thái")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_bookings'

    def __str__(self):
        return f"{self.customer.full_name} - {self.booking_date} {self.start_time}"

class BookingStatus(models.Model):
    STATUS_CHOICES = [
        ('Booked', 'Booked'),
        ('CheckedIn', 'CheckedIn'),
        ('Paid', 'Paid'),
        ('Cancelled', 'Cancelled'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    changed_by = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_booking_status'

    def __str__(self):
        return f"{self.booking.id} - {self.status}"

class BookingBill(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('QR Code', 'QR Code'),
        ('Cash', 'Cash'),
        ('Card', 'Card'),
    ]
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='bill')
    payment_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Số tiền")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='QR Code', verbose_name="Phương thức")
    customer_rating = models.IntegerField(blank=True, null=True, choices=[(i, i) for i in range(1, 6)])
    customer_review = models.TextField(blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_booking_bill'

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

class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    slug = models.SlugField(max_length=255, unique=True)
    content = models.TextField(verbose_name="Nội dung")
    thumbnail_url = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_articles'

    def __str__(self):
        return self.title
