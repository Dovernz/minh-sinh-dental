import re
with open('/app/booking/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = re.sub(
    r'class Service\(models\.Model\):.*?def __str__\(self\):\n        return self\.name',
    '''class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên danh mục")
    estimate_time = models.IntegerField(default=30, verbose_name="Thời gian ước tính (phút)")
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_service_categories'
        verbose_name = 'Danh mục Dịch vụ'
        verbose_name_plural = 'Danh mục Dịch vụ'

    def __str__(self):
        return self.name

class ServiceDetail(models.Model):
    DIFFICULTY_CHOICES = [
        ('Cơ bản', 'Cơ bản'),
        ('Dễ', 'Dễ'),
        ('Trung bình', 'Trung bình'),
        ('Khó', 'Khó'),
        ('Phức tạp', 'Phức tạp'),
    ]
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services', verbose_name='Danh mục')
    code = models.CharField(max_length=20, unique=True, verbose_name='Mã dịch vụ')
    name = models.CharField(max_length=255, verbose_name='Tên dịch vụ chi tiết')
    difficulty = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES, default='Cơ bản', verbose_name='Độ khó')
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name='Giá')
    warranty = models.CharField(max_length=100, null=True, blank=True, verbose_name='Bảo hành')
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'db_table_service_details'
        verbose_name = 'Chi tiết Dịch vụ'
        verbose_name_plural = 'Chi tiết Dịch vụ'

    def __str__(self):
        return f"{self.code} - {self.name}"''',
    text, flags=re.DOTALL
)

with open('/app/booking/models.py', 'w', encoding='utf-8') as f:
    f.write(text)