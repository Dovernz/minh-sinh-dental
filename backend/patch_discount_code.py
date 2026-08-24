import re

with open('/app/booking/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('    code = models.CharField(max_length=50, verbose_name="Mã giảm giá")', '    code = models.CharField(max_length=50, unique=True, verbose_name="Mã giảm giá")')

with open('/app/booking/models.py', 'w', encoding='utf-8') as f:
    f.write(text)