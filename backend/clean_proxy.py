import re

with open('/app/booking/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

proxy = '''
class CatalogDiscount(Discount):
    class Meta:
        proxy = True
        app_label = "services_menu"
        verbose_name = "Khuyến mãi"
        verbose_name_plural = "Khuyến mãi"
'''
text = text.replace(proxy, '')

with open('/app/booking/models.py', 'w', encoding='utf-8') as f:
    f.write(text)