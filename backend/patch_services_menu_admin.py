import re

with open('/app/services_menu/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

new_admin = '''
from services_menu.models import CatalogDiscount

@admin.register(CatalogDiscount)
class CatalogDiscountAdmin(BaseRBACAdmin):
    list_display = ('code', 'description', 'discount_type', 'value', 'is_active')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code', 'description')
'''
text += new_admin

with open('/app/services_menu/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)