import sys

with open('/app/booking/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

index = text.find('class Discount(models.Model):')
if index != -1:
    text = text[:index]
    with open('/app/booking/models.py', 'w', encoding='utf-8') as f:
        f.write(text)