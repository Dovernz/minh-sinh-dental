# -*- coding: utf-8 -*-
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib import admin
from django.db.models import Sum

class Clinic(models.Model):
    clinic_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="TÃªn chi nhÃ¡nh")
    address = models.TextField(blank=True, null=True, verbose_name="Äá»‹a chá»‰")
    hotline = models.CharField(max_length=12, blank=True, null=True, verbose_name="Hotline")
    map_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Link Google Map")
    total_chairs = models.IntegerField(default=5, verbose_name="Tá»•ng sá»‘ gháº¿")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_clinic'

    def __str__(self):
        return str(self.name)

class ServiceCategory(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, verbose_name="TÃªn danh má»¥c")
    estimate_time = models.IntegerField(default=30, verbose_name="Thá»i gian Æ°á»›c tÃ­nh (phÃºt)")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_service_categories'
        verbose_name = 'Danh má»¥c Dá»‹ch vá»¥'
        verbose_name_plural = 'Danh má»¥c Dá»‹ch vá»¥'

    def __str__(self):
        return str(self.name)

class ServiceDetail(models.Model):
    service_id = models.AutoField(primary_key=True)
    DIFFICULTY_CHOICES = [
        ('CÆ¡ báº£n', 'CÆ¡ báº£n'),
        ('Dá»…', 'Dá»…'),
        ('Trung bÃ¬nh', 'Trung bÃ¬nh'),
        ('KhÃ³', 'KhÃ³'),
        ('Phá»©c táº¡p', 'Phá»©c táº¡p'),
    ]
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name='Danh má»¥c')
    code = models.CharField(max_length=20, null=True, blank=True, verbose_name='MÃ£ dá»‹ch vá»¥')
    name = models.CharField(max_length=255, verbose_name='TÃªn dá»‹ch vá»¥ chi tiáº¿t')
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, default='CÆ¡ báº£n', verbose_name='Äá»™ khÃ³')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='GiÃ¡')
    warranty = models.CharField(max_length=100, null=True, blank=True, verbose_name='Báº£o hÃ nh')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_service_details'
        verbose_name = 'Chi tiáº¿t Dá»‹ch vá»¥'
        verbose_name_plural = 'Chi tiáº¿t Dá»‹ch vá»¥'
        constraints = [
            models.UniqueConstraint(fields=['category', 'name'], name='unique_service_detail')
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"

class TimeSlot(models.Model):
    timeslot_id = models.AutoField(primary_key=True)
    start_time = models.TimeField(verbose_name="Thá»i gian báº¯t Ä‘áº§u")
    end_time = models.TimeField(verbose_name="Thá»i gian káº¿t thÃºc")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_time_slots'

    def __str__(self):
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    patient_code = models.CharField(max_length=50, unique=True, null=True, blank=True, verbose_name="MÃ£ bá»‡nh nhÃ¢n")
    name = models.CharField(max_length=100, verbose_name="Há» vÃ  tÃªn")
    phone = models.CharField(max_length=12, unique=True, verbose_name="Sá»‘ Ä‘iá»‡n thoáº¡i")
    customer_dob = models.DateField(blank=True, null=True, verbose_name="NgÃ y sinh")
    gender = models.CharField(max_length=10, blank=True, null=True, verbose_name="Giá»›i tÃ­nh")
    address = models.TextField(blank=True, null=True, verbose_name="Äá»‹a chá»‰")
    email = models.EmailField(max_length=100, blank=True, null=True, verbose_name="Email")
    created_on = models.DateTimeField(auto_now_add=True)

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
    full_name = models.CharField(max_length=255, verbose_name="Há» vÃ  tÃªn")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Sá»‘ Ä‘iá»‡n thoáº¡i")
    email = models.EmailField(max_length=50, blank=True, null=True, verbose_name="Email")
    specialty = models.CharField(max_length=50, blank=True, null=True, verbose_name="ChuyÃªn mÃ´n")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='Doctor', verbose_name="Vai trÃ²")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_employees'

    def __str__(self):
        return self.full_name

class Booking(models.Model):
    booking_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='bookings')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='bookings')
    category = models.ForeignKey(ServiceCategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Danh má»¥c")
    start_time = models.DateTimeField(null=True, blank=True, verbose_name="Giá» báº¯t Ä‘áº§u")
    end_time = models.DateTimeField(null=True, blank=True, verbose_name="Giá» káº¿t thÃºc")
    status = models.CharField(max_length=20, default='Pending', verbose_name="Tráº¡ng thÃ¡i")
    notes = models.TextField(blank=True, null=True, verbose_name="Ghi chÃº")
    created_on = models.DateTimeField(auto_now_add=True)
    created_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_bookings', help_text='NhÃ¢n viÃªn táº¡o booking (Null náº¿u khÃ¡ch tá»± Ä‘áº·t trÃªn web)')

    estimated_duration = models.IntegerField(null=True, blank=True, help_text='Thá»i lÆ°á»£ng dá»± kiáº¿n (phÃºt)')
    class Meta:
        db_table = 'db_table_bookings'

    def __str__(self):
        return f"{self.customer.name} - {self.start_time}"

class BookingStatusHistory(models.Model):
    status_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, verbose_name="Tráº¡ng thÃ¡i")
    created_at = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chÃº")

    class Meta:
        db_table = 'db_table_booking_status_history'

    def __str__(self):
        return f"{self.booking.booking_id} - {self.status}"

class Payment(models.Model):
    payment_id = models.AutoField(primary_key=True)
    PAYMENT_METHOD_CHOICES = [
        ('QR Code', 'QR Code'),
        ('Cash', 'Cash'),
        ('Card', 'Card'),
    ]
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Sá»‘ tiá»n")
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES, default='QR Code', verbose_name="PhÆ°Æ¡ng thá»©c")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_payments'

    def __str__(self):
        return f"{self.booking.id} - {self.amount}"

class InventoryDetail(models.Model):
    item_id = models.AutoField(primary_key=True)
    item_name = models.CharField(max_length=255, verbose_name="TÃªn váº­t tÆ°")
    unit = models.CharField(max_length=50, verbose_name="ÄÆ¡n vá»‹ tÃ­nh")
    category = models.CharField(max_length=100, blank=True, null=True, verbose_name="PhÃ¢n loáº¡i")
    price_per_unit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="GiÃ¡ vá»‘n")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_inventory_details'

    def __str__(self):
        return self.item_name

class InventoryUsage(models.Model):
    usage_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='inventory_usages')
    item = models.ForeignKey(InventoryDetail, on_delete=models.RESTRICT, related_name='usages')
    quantity_used = models.PositiveIntegerField(verbose_name="Sá»‘ lÆ°á»£ng dÃ¹ng")
    employee = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="NgÆ°á»i xuáº¥t/sá»­ dá»¥ng")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_inventory_usage'

from ckeditor_uploader.fields import RichTextUploadingField

class Article(models.Model):
    article_id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ('Draft', 'Báº£n nhÃ¡p'),
        ('Published', 'Xuáº¥t báº£n')
    ]
    title = models.CharField(max_length=255, verbose_name="TiÃªu Ä‘á»")
    slug = models.SlugField(max_length=255, unique=True)
    content = RichTextUploadingField(verbose_name="Ná»™i dung")
    thumbnail_url = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft', verbose_name="Tráº¡ng thÃ¡i")
    word_file = models.FileField(upload_to='temp/', null=True, blank=True, verbose_name="Táº£i lÃªn File Word (.docx)")
    
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
    topup_id = models.AutoField(primary_key=True)
    bank_name = models.CharField(max_length=50, verbose_name='TÃªn ngÃ¢n hÃ ng (MÃ£)')
    account_number = models.CharField(max_length=50, verbose_name='Sá»‘ tÃ i khoáº£n')
    account_name = models.CharField(max_length=100, verbose_name='TÃªn tÃ i khoáº£n')
    is_default = models.BooleanField(default=False, verbose_name='Máº·c Ä‘á»‹nh')

    class Meta:
        db_table = 'db_table_topup_info'
        verbose_name = 'Cáº¥u hÃ¬nh Thanh toÃ¡n'
        verbose_name_plural = 'Cáº¥u hÃ¬nh Thanh toÃ¡n'

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
        verbose_name = 'Báº£ng chi tiáº¿t'
        verbose_name_plural = 'Báº£ng chi tiáº¿t'


class Discount(models.Model):
    discount_id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=50, unique=True, verbose_name="MÃ£ giáº£m giÃ¡")
    description = models.TextField(blank=True, null=True, verbose_name="MÃ´ táº£")
    discount_type = models.CharField(max_length=20, choices=[("Percent", "Pháº§n trÄƒm"), ("Fixed", "Sá»‘ tiá»n")], default="Percent", verbose_name="Loáº¡i giáº£m giÃ¡")
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="GiÃ¡ trá»‹")
    is_active = models.BooleanField(default=True, verbose_name="Tráº¡ng thÃ¡i")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "db_table_discounts"
        verbose_name = "Khuyáº¿n mÃ£i"
        verbose_name_plural = "Khuyáº¿n mÃ£i"

    def __str__(self):
        return f"{self.code} ({self.value} {self.discount_type})"

class BookingDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey("Booking", on_delete=models.CASCADE, related_name="details")
    service_detail = models.ForeignKey("ServiceDetail", on_delete=models.SET_NULL, null=True, verbose_name="Dá»‹ch vá»¥")
    doctor = models.ForeignKey("Employee", on_delete=models.SET_NULL, null=True, limit_choices_to={'role': 'Doctor'}, verbose_name="BÃ¡c sÄ© khÃ¡m")
    actual_price = models.IntegerField(null=True, blank=True, verbose_name="ÄÆ¡n giÃ¡")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Sá»‘ lÆ°á»£ng")

    class Meta:
        db_table = "db_table_booking_details"
        verbose_name = "Dá»‹ch vá»¥ trong Lá»‹ch"
        verbose_name_plural = "CÃ¡c dá»‹ch vá»¥"

    def save(self, *args, **kwargs):
        if not self.actual_price and self.service_detail:
            self.actual_price = self.service_detail.price or 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking.booking_id} - {self.service_detail.name if self.service_detail else ''}"

class Billing(models.Model):
    billing_id = models.AutoField(primary_key=True)
    booking = models.OneToOneField("Booking", on_delete=models.CASCADE, related_name="billing", verbose_name="Lá»‹ch khÃ¡m")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tá»•ng tiá»n gá»‘c (Há»‡ thá»‘ng tÃ­nh)")
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Khuyáº¿n mÃ£i")
    adjustment = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Sá»‘ tiá»n Ä‘iá»u chá»‰nh")
    final_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Sá»‘ tiá»n cuá»‘i cÃ¹ng")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "db_table_billing"
        verbose_name = "HÃ³a Ä‘Æ¡n Káº¿ toÃ¡n"
        verbose_name_plural = "HÃ³a Ä‘Æ¡n Káº¿ toÃ¡n"

    def save(self, *args, **kwargs):
        discount_amount = 0
        if self.discount and self.discount.is_active:
            if self.discount.discount_type == "Percent":
                discount_amount = (self.sub_total * self.discount.value) / 100
            else:
                discount_amount = self.discount.value

        calculated_total = self.sub_total - discount_amount
        if calculated_total < 0:
            calculated_total = 0

        if self.final_total and self.final_total > 0 and self.final_total != calculated_total:
            self.adjustment = self.final_total - calculated_total
        else:
            self.adjustment = 0
            self.final_total = calculated_total

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill #{self.billing_id} - Booking {self.booking.booking_id}"

