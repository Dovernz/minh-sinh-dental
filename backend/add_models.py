new_models = '''
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

class CatalogDiscount(Discount):
    class Meta:
        proxy = True
        app_label = "services_menu"
        verbose_name = "Khuyến mãi"
        verbose_name_plural = "Khuyến mãi"

class BookingDetail(models.Model):
    detail_id = models.AutoField(primary_key=True)
    booking = models.ForeignKey("Booking", on_delete=models.CASCADE, related_name="details")
    service = models.ForeignKey("ServiceDetail", on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Đơn giá")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Số lượng")

    class Meta:
        db_table = "db_table_booking_details"
        verbose_name = "Dịch vụ trong Lịch"
        verbose_name_plural = "Các dịch vụ"

    def save(self, *args, **kwargs):
        if not self.price and self.service:
            self.price = self.service.price or 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.booking.booking_id} - {self.service.name if self.service else ''}"

class Billing(models.Model):
    billing_id = models.AutoField(primary_key=True)
    booking = models.OneToOneField("Booking", on_delete=models.CASCADE, related_name="billing", verbose_name="Lịch khám")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tổng tiền gốc (Hệ thống tính)")
    discount = models.ForeignKey(Discount, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Khuyến mãi")
    manual_total = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Tổng tiền thu thực tế (Nhập tay)")
    adjustment = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Số tiền điều chỉnh")
    final_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Số tiền cuối cùng")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "db_table_billing"
        verbose_name = "Hóa đơn Kế toán"
        verbose_name_plural = "Hóa đơn Kế toán"

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

        if self.manual_total is not None:
            self.adjustment = self.manual_total - calculated_total
            self.final_total = self.manual_total
        else:
            self.adjustment = 0
            self.final_total = calculated_total

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Bill #{self.billing_id} - Booking {self.booking.booking_id}"
'''

with open('/app/booking/models.py', 'a', encoding='utf-8') as f:
    f.write(new_models)