import re

def add_filter(file_path, admin_class, existing_filter):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    if 'class PriceRangeFilter' not in text:
        filter_code = '''
class PriceRangeFilter(admin.SimpleListFilter):
    title = 'Khoảng giá'
    parameter_name = 'price_range'

    def lookups(self, request, model_admin):
        return (
            ('under_1m', 'Dưới 1 triệu'),
            ('1m_to_5m', 'Từ 1 triệu - 5 triệu'),
            ('over_5m', 'Trên 5 triệu'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'under_1m':
            return queryset.filter(price__lt=1000000)
        if self.value() == '1m_to_5m':
            return queryset.filter(price__gte=1000000, price__lte=5000000)
        if self.value() == 'over_5m':
            return queryset.filter(price__gt=5000000)
        return queryset
'''
        text = text.replace('class ' + admin_class, filter_code + '\nclass ' + admin_class)

    # Replace list_filter
    text = text.replace(existing_filter, "list_filter = ['category', 'difficulty', PriceRangeFilter]")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(text)

add_filter('/app/booking/admin.py', 'ServiceDetailAdmin', "list_filter = ('difficulty', 'category')")
add_filter('/app/services_menu/admin.py', 'CatalogServiceDetailAdmin', "list_filter = ('category', 'difficulty')")
