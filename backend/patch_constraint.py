import re
with open('/app/booking/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    \"verbose_name_plural = 'Chi tiết Dịch vụ'\",
    \"verbose_name_plural = 'Chi tiết Dịch vụ'\n        constraints = [\n            models.UniqueConstraint(fields=['category', 'name'], name='unique_service_detail')\n        ]\"
)

with open('/app/booking/models.py', 'w', encoding='utf-8') as f:
    f.write(text)