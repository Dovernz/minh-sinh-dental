from django.utils import timezone
import requests
# -*- coding: utf-8 -*-
from django.db import models
from cloudinary.models import CloudinaryField
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models import Sum

class Clinic(models.Model):
    clinic_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Tên chi nhánh")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    hotline = models.CharField(max_length=12, blank=True, null=True, verbose_name="Hotline")
    map_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Link Google Map")
    total_chairs = models.IntegerField(default=5, verbose_name="Tổng số ghế")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_clinic'

    def __str__(self):
        return str(self.name)

class ServiceCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    estimate_time = models.IntegerField(default=30, verbose_name="Thời gian ước tính (phút)")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_service_categories'
        verbose_name = 'Danh mục Dịch vụ'
        verbose_name_plural = 'Danh mục Dịch vụ'

    def __str__(self):
        return str(self.name)

class ServiceDetail(models.Model):
    service_id = models.AutoField(primary_key=True)
    DIFFICULTY_CHOICES = [
        ('Cơ bản', 'Cơ bản'),
        ('Dễ', 'Dễ'),
        ('Trung bình', 'Trung bình'),
        ('Khó', 'Khó'),
        ('Phức tạp', 'Phức tạp'),
    ]
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name='Danh mục')
    code = models.CharField(max_length=20, null=True, blank=True, verbose_name='Mã dịch vụ')
    name = models.CharField(max_length=255, verbose_name='Tên dịch vụ chi tiết')
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, default='Cơ bản', verbose_name='Độ khó')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Giá')
    warranty = models.CharField(max_length=100, null=True, blank=True, verbose_name='Bảo hành')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_service_details'
        verbose_name = 'Chi tiết Dịch vụ'
        verbose_name_plural = 'Chi tiết Dịch vụ'
        constraints = [
            models.UniqueConstraint(fields=['category', 'name'], name='unique_service_detail')
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

class TimeSlot(models.Model):
    timeslot_id = models.AutoField(primary_key=True)
    start_time = models.TimeField(verbose_name="Thời gian bắt đầu")
    end_time = models.TimeField(verbose_name="Thời gian kết thúc")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_time_slots'

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    patient_code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="Mã bệnh nhân")
    name = models.CharField(max_length=100, verbose_name="Họ và tên")
    phone = models.CharField(max_length=12, unique=True, verbose_name="Số điện thoại")
    customer_dob = models.DateField(blank=True, null=True, verbose_name="Ngày sinh")
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name="Giới tính")
    address = models.TextField(blank=True, null=True, verbose_name="Địa chỉ")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Email")
    created_on = models.DateTimeField(auto_now_add=True)
    customer_type = models.CharField(max_length=20, choices=[("Mới", "Khách Mới"), ("Cũ", "Khách Cũ")], default="Mới", verbose_name="Phân loại Khách")
    medical_notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú bệnh nhân")
    customer_source = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nguồn KH")
    source_detail = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nguồn chi tiết")
    nationality = models.CharField(max_length=255, blank=True, null=True, verbose_name="Quốc tịch")
    profession = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nghề nghiệp")
    city = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tỉnh/Thành phố")
    district = models.CharField(max_length=255, blank=True, null=True, verbose_name="Phường xã")
    identity_card = models.CharField(max_length=255, blank=True, null=True, verbose_name="CMND/CC")
    id_issue_date = models.DateField(blank=True, null=True, verbose_name="Ngày cấp CMND")
    id_issue_place = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nơi cấp")
    insurance_type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Đối tượng bảo hiểm")
    insurance_code = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mã bảo hiểm")
    
    # VTTech specific fields
    facebook_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="Facebook")
    zalo_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="Zalo")
    viber_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="Viber")
    instagram_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="Instagram")
    gdrive_link = models.CharField(max_length=255, blank=True, null=True, verbose_name="GDrive")
    phone_2 = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại 2")
    passport = models.CharField(max_length=255, blank=True, null=True, verbose_name="Hộ chiếu")
    ethnicity = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dân tộc")
    religion = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tôn giáo")
    marketing_staff = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nhân viên marketing")
    gclid = models.CharField(max_length=255, blank=True, null=True, verbose_name="Gclid")
    dvqhns = models.CharField(max_length=255, blank=True, null=True, verbose_name="ĐVQHNS")
    language = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ngôn ngữ")
    expected_clinic = models.CharField(max_length=255, blank=True, null=True, verbose_name="Chi nhánh dự kiến")
    old_customer_code = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mã khách cũ")
    general_note = models.TextField(blank=True, null=True, verbose_name="Ghi chú chung")

    class Meta:
        db_table = 'db_table_customers'

    def __str__(self):
        return str(self.name)

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    ROLE_CHOICES = [
        ('Admin', 'Admin'),
        ('Doctor', 'Doctor'),
        ('Reception', 'Reception'),
        ('Marketing', 'Marketing'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile', blank=True, null=True)
    full_name = models.CharField(max_length=255, verbose_name="Họ và tên")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    email = models.EmailField(max_length=50, blank=True, null=True, verbose_name='Email')
    dob = models.DateField(null=True, blank=True, verbose_name='Ngày sinh')
    company_email = models.EmailField(max_length=50, blank=True, null=True, verbose_name='Mail công ty')
    nickname = models.CharField(max_length=100, blank=True, null=True, verbose_name='Nickname')
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name='Bộ phận')
    is_all_clinics = models.BooleanField(default=True, verbose_name='Tất cả chi nhánh')
    clinic = models.ForeignKey('Clinic', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Chi nhánh')
    specialty = models.CharField(max_length=50, blank=True, null=True, verbose_name="Chuyên môn")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Doctor', verbose_name="Vai trò")
    contract_type = models.CharField(max_length=20, choices=[('Part-time', 'Part-time'), ('Full-time', 'Full-time')], default='Full-time')
    allowance_position = models.IntegerField(default=0, verbose_name='Phụ cấp chức vụ')
    allowance_degree = models.IntegerField(default=0, verbose_name='Phụ cấp bằng cấp')
    allowance_specialty = models.IntegerField(default=0, verbose_name='Phụ cấp chuyên môn')
    annual_leave_days = models.IntegerField(default=0, verbose_name='Số ngày phép năm')
    used_leave_days = models.IntegerField(default=0, verbose_name='Ngày phép đã sử dụng')
    start_date = models.DateField(null=True, blank=True, verbose_name='Ngày nhận việc')
    base_salary = models.IntegerField(default=0, verbose_name='Lương căn bản')
    agreed_salary = models.IntegerField(default=0, verbose_name='Lương thỏa thuận')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_employees'

    def __str__(self):
        return self.full_name

class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='bookings')
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Danh mục")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="Giờ bắt đầu")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Giờ kết thúc")
    status = models.CharField(max_length=20, default='Pending', verbose_name="Trạng thái")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    created_on = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_bookings', help_text='Nhân viên tạo booking (Null nếu khách tự đặt trên web)')

    estimated_duration = models.IntegerField(null=True, blank=True, help_text='Thời lượng dự kiến (phút)')
    class Meta:
        db_table = 'db_table_bookings'

    def __str__(self):
        return f"{self.customer.name} - {self.start_time}"

class BookingStatusHistory(models.Model):
    status_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    class Meta:
        db_table = 'db_table_booking_status_history'

    def __str__(self):
        return f"{self.booking.booking_id} - {self.status}"

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    billing = models.ForeignKey('Billing', on_delete=models.CASCADE, related_name='payments', null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Số tiền thanh toán")
    payment_method = models.CharField(max_length=20, choices=[('CASH', 'Tiền mặt'), ('QR', 'Chuyển khoản QR'), ('CREDIT', 'Quẹt thẻ')], default='CASH')
    total_billing = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Tổng tiền Hóa đơn", default=0)
    amount_remain = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Dư nợ còn lại", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_payments'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.amount_remain <= 0 and self.billing:
            from django.utils import timezone
            booking = self.billing.booking
            if booking and booking.status != 'Completed':
                booking.status = 'Completed'
                booking.save(update_fields=['status'])
            
            if self.billing.status != 'PAID':
                self.billing.status = 'PAID'
                self.billing.save(update_fields=['status'])
class InventoryDetail(models.Model):
    item_id = models.AutoField(primary_key=True)
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
    usage_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='inventory_usages')
    item = models.ForeignKey(InventoryDetail, on_delete=models.RESTRICT, related_name='usages')
    quantity_used = models.PositiveIntegerField(verbose_name="Số lượng dùng")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người xuất/sử dụng")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_inventory_usage'

from tinymce.models import HTMLField

class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('Draft', 'Bản nháp'),
        ('Published', 'Xuất bản')
    ]
    title = models.CharField(max_length=255, verbose_name="Tiêu đề")
    slug = models.SlugField(max_length=255, unique=True)
    content = HTMLField(verbose_name="Nội dung")
    thumbnail = CloudinaryField("Ảnh Thumbnail (Tải lên)", blank=True, null=True)
    show_banner = models.BooleanField(default=True, verbose_name="Hiển thị Banner bài viết")
    banner_image = models.FileField(upload_to="raw/upload/", null=True, blank=True, verbose_name="Ảnh Banner riêng (Trống = dùng Thumbnail)")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft', verbose_name="Trạng thái")
    category = models.ForeignKey('MenuLink', on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'parent__isnull': False}, verbose_name="Chuyên mục (Menu gốc)")

    word_file = CloudinaryField('Tài liệu Word', resource_type='raw', blank=True, null=True)
    
    # SEO fields
    meta_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="SEO Title")
    meta_description = models.TextField(blank=True, null=True, verbose_name="SEO Description")
    focus_keyword = models.CharField(max_length=255, blank=True, null=True, verbose_name="Focus Keyword")
    
    created_on = models.DateTimeField(auto_now_add=True)
    def get_absolute_url(self):
        if getattr(self, 'status', '') == 'Draft':
            return f"http://localhost:3000/blog-demo/{self.slug}?preview=admin_secret_123"
        return f"http://localhost:3000/blog/{self.slug}"


    class Meta:
        db_table = 'db_table_articles'

    def __str__(self):
        return self.title



class TopupInfo(models.Model):
    topup_id = models.AutoField(primary_key=True)
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


class CatalogServiceDetail(ServiceDetail):
    class Meta:
        proxy = True
        app_label = 'services_menu'
        verbose_name = 'Bảng chi tiết'
        verbose_name_plural = 'Bảng chi tiết'


class Discount(models.Model):
    discount_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã giảm giá")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    discount_type = models.CharField(max_length=20, choices=[("Percent", "Phần trăm"), ("Fixed", "Số tiền")], default="Percent", verbose_name="Loại giảm giá")
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá trị")
    is_active = models.BooleanField(default=True, verbose_name="Trạng thái")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "db_table_discounts"
        verbose_name = "Khuyến mãi"
        verbose_name_plural = "Khuyến mãi"

    def __str__(self):
        return f"{self.code} ({self.value} {self.discount_type})"

class BookingDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey("Booking", on_delete=models.CASCADE, related_name="details")
    service_detail = models.ForeignKey("ServiceDetail", on_delete=models.SET_NULL, null=True, verbose_name="Dịch vụ")
    consulting_doctor = models.ForeignKey("Employee", on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'Doctor'}, related_name='consulting_details', verbose_name="Bác sĩ tư vấn")
    performing_doctor = models.ForeignKey("Employee", on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'Doctor'}, related_name='performing_details', verbose_name="Bác sĩ thực hiện")
    actual_price = models.IntegerField(null=True, blank=True, verbose_name="Đơn giá")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")
    tooth_position = models.CharField(max_length=50, null=True, blank=True, verbose_name="Vị trí răng")
    consulting_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Hoa hồng tư vấn")
    performing_commission = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Hoa hồng thực hiện")

    class Meta:
        db_table = "db_table_booking_details"
        verbose_name_plural = "Chi tiết Booking"

    def save(self, *args, **kwargs):
        if not self.actual_price and self.service_detail:
            self.actual_price = self.service_detail.price or 0
            
        from decimal import Decimal
        if self.consulting_doctor and self.consulting_doctor.contract_type == 'Part-time':
            self.consulting_commission = Decimal(self.actual_price or 0) * Decimal('0.05')
        else:
            self.consulting_commission = Decimal('0')

        if self.performing_doctor and self.performing_doctor.contract_type == 'Part-time':
            self.performing_commission = Decimal(self.actual_price or 0) * Decimal('0.10')
        else:
            self.performing_commission = Decimal('0')

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking.booking_id} - {self.service_detail.name if self.service_detail else ''}"

class Billing(models.Model):
    clinic = models.ForeignKey('Clinic', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Cơ sở khám')
    billing_id = models.AutoField(primary_key=True)
    booking = models.OneToOneField("Booking", on_delete=models.CASCADE, related_name="billing", verbose_name="Lịch khám")
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Tổng tiền gốc")
    discount = models.ForeignKey('Discount', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Mã giảm giá")
    adjustment = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Điều chỉnh (+/-)")
    final_total = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Thành tiền")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú thu ngân")
    payment_method = models.CharField(max_length=20, choices=[('CASH', 'Tiền mặt'), ('QR', 'Chuyển khoản QR'), ('CREDIT', 'Quẹt thẻ')], default='CASH', verbose_name="Phương thức")
    status = models.CharField(max_length=20, choices=[('UNPAID', 'Chưa thanh toán'), ('INSTALLMENT', 'Trả góp/Còn nợ'), ('PAID', 'Đã thanh toán hoàn tất')], default='UNPAID', verbose_name="Trạng thái")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "db_table_billing"
        verbose_name = "Hóa đơn Kế toán"
        verbose_name_plural = "Hóa đơn Kế toán"

    def save(self, *args, **kwargs):
        discount_amount = 0
        if self.discount and self.discount.is_active:
            if self.discount.discount_type == "Percent":
                discount_amount = (self.subtotal * self.discount.value) / 100
            else:
                discount_amount = self.discount.value

        calculated_total = self.subtotal - discount_amount
        if calculated_total < 0:
            calculated_total = 0

        if self.final_total and self.final_total > 0 and self.final_total != calculated_total:
            self.adjustment = self.final_total - calculated_total
        else:
            self.adjustment = 0
            self.final_total = calculated_total

        super().save(*args, **kwargs)

        if self.status == 'PAID':
            from django.utils import timezone
            if self.booking and self.booking.status != 'Completed':
                self.booking.status = 'Completed'
                self.booking.save(update_fields=['status'])

    def __str__(self):
        return f"Bill #{self.billing_id} - Booking {self.booking.booking_id}"

class MenuLink(models.Model):
    title = models.CharField(max_length=100, verbose_name="Tiêu đề Menu")
    url = models.CharField(max_length=255, verbose_name="Đường dẫn (URL)")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name="Menu Cha (Để trống nếu là Menu gốc)")
    order = models.IntegerField(default=0, verbose_name="Thứ tự")
    is_active = models.BooleanField(default=True, verbose_name="Hiển thị")

    class Meta:
        db_table = 'db_table_menulink'
        ordering = ['order']
        verbose_name = "Cấu hình Header"
        verbose_name_plural = "Cấu hình Header"

    def __str__(self):
        return f"{self.parent.title} > {self.title}" if self.parent else self.title

class SiteSettings(models.Model):
    email = models.EmailField(default="contact@minhsinhdental.com", verbose_name="Email")
    working_hours = models.CharField(max_length=255, default="08:00 - 18:00 (Thứ 2 - CN)", verbose_name="Giờ làm việc")
    branch_section_title = models.CharField(max_length=100, default="HỆ THỐNG CƠ SỞ", verbose_name="Tiêu đề Cột Cơ sở")
    social_section_title = models.CharField(max_length=100, default="KẾT NỐI VỚI CHÚNG TÔI", verbose_name="Tiêu đề Cột MXH")
    
    class Meta:
        db_table = 'db_table_sitesettings'
        verbose_name = "Cấu hình Footer"
        verbose_name_plural = "Cấu hình Footer"
        
    def __str__(self):
        return "Chi tiết Cấu hình Footer"

class ClinicBranch(models.Model):
    settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, related_name='branches')
    name = models.CharField(max_length=100, default="Cơ sở 1", verbose_name="Tên cơ sở (VD: Trụ sở chính)")
    address = models.CharField(max_length=255, verbose_name="Địa chỉ")
    hotline = models.CharField(max_length=20, verbose_name="Hotline")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    
    class Meta:
        db_table = 'db_table_clinicbranch'
        ordering = ['order']

class SocialLink(models.Model):
    settings = models.ForeignKey(SiteSettings, on_delete=models.CASCADE, related_name='social_links')
    name = models.CharField(max_length=50, verbose_name="Tên MXH (VD: Facebook, Zalo)")
    url = models.URLField(verbose_name="Đường dẫn")
    order = models.IntegerField(default=0, verbose_name="Thứ tự")
    
    class Meta:
        db_table = 'db_table_sociallink'
        ordering = ['order']


# ==========================================
# MODULE TƯ VẤN & PHÁC ĐỒ (DOCTOR CONSULTATION)
# ==========================================
class Consultation(models.Model):
    consultation_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='consultations', verbose_name="Khách hàng")
    clinic = models.ForeignKey(Clinic, on_delete=models.SET_NULL, null=True, verbose_name="Cơ sở khám")
    doctor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'Doctor'}, verbose_name="Bác sĩ tư vấn")
    created_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chú tổng quát")
    
    class Meta:
        db_table = 'db_table_consultations'
        verbose_name = "Hồ sơ Tư vấn"
        verbose_name_plural = "Hồ sơ Tư vấn"

class ConsultationDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='details')
    service_detail = models.ForeignKey(ServiceDetail, on_delete=models.SET_NULL, null=True)
    tooth_position = models.CharField(max_length=50, blank=True, null=True, verbose_name="Vị trí răng")
    notes = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ghi chú")
    proposed_price = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Giá đề xuất")
    is_accepted = models.BooleanField(default=False, verbose_name='Khách chốt làm')
    consulting_doctor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='consulting_consultations', verbose_name='Bác sĩ tư vấn')
    performing_doctor = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, related_name='performing_consultations', verbose_name='Bác sĩ thực hiện')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Số lượng')
    discount = models.IntegerField(default=0, verbose_name='Chiết khấu')
    vat_percent = models.IntegerField(default=0, verbose_name='VAT (%)')
    discount_amount = models.IntegerField(default=0, verbose_name='Tiền C.Khấu')
    discount_reason = models.CharField(max_length=255, blank=True, null=True, verbose_name='Lý do giảm giá')
    
    @property
    def final_price(self):
        from decimal import Decimal
        return Decimal(self.proposed_price or 0) - Decimal(self.discount_amount or 0)

    class Meta:
        db_table = 'db_table_consultation_details'

class DoctorConsultationProxy(Consultation):
    class Meta:
        proxy = True
        verbose_name = 'Phác đồ & Tư vấn (Bác sĩ)'
        verbose_name_plural = 'Phác đồ & Tư vấn (Bác sĩ)'


class DentalChart(models.Model):
    """So do rang - JSON format for easy versioning"""
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name='dental_charts',
        verbose_name='Khach hang'
    )
    sequence_num = models.IntegerField(default=1, verbose_name='Phien ban so')
    cloned_from = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clones',
        verbose_name='Phien ban goc'
    )
    tooth_data = models.JSONField(default=dict, verbose_name='Du lieu so do rang')
    notes_data = models.JSONField(default=dict, blank=True, null=True, verbose_name='Du lieu ghi chu')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Ngay tao')

    class Meta:
        db_table = 'db_table_dental_charts'
        verbose_name = 'Phien ban So do rang'
        verbose_name_plural = 'Phien ban So do rang'
        unique_together = ('customer', 'sequence_num')

    def __str__(self):
        return f'Chart KH {self.customer_id} - Ver {self.sequence_num}'






class CommissionRate(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên kỳ hoa hồng")
    start_date = models.DateField(verbose_name="Từ ngày", default=timezone.now)
    end_date = models.DateField(verbose_name="Đến ngày", null=True, blank=True)
    performing_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=10, verbose_name="% Thực hiện")
    consulting_rate_percent = models.DecimalField(max_digits=5, decimal_places=2, default=5, verbose_name="% Tư vấn")

    class Meta:
        db_table = 'db_table_commission_rates'
        verbose_name = 'Tỷ lệ hoa hồng'
        verbose_name_plural = 'Tỷ lệ hoa hồng'

    def __str__(self):
        end = self.end_date.strftime('%Y-%m-%d') if self.end_date else 'Vô thời hạn'
        return f"{self.name} ({self.start_date.strftime('%Y-%m-%d')} - {end})"
