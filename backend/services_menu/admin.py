from django.contrib import admin
from booking.models import CatalogServiceDetail
from operations.admin import BaseRBACAdmin

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

@admin.register(CatalogServiceDetail)
class CatalogServiceDetailAdmin(BaseRBACAdmin):
    list_display = ('category', 'code', 'name', 'difficulty', 'formatted_price', 'warranty')
    list_filter = ['category', 'difficulty', PriceRangeFilter]
    search_fields = ['category__name', 'code', 'name', 'difficulty', 'price', 'warranty']
    ordering = ('category', 'code')
    list_display_links = ('code', 'name')
    
    def formatted_price(self, obj):
        if obj.price is not None:
            return f"{int(obj.price):,} ₫".replace(',', '.')
        return ''
    formatted_price.short_description = 'Giá'
    

    def get_search_results(self, request, queryset, search_term):
        original_search_fields = self.search_fields
        self.search_fields = [f for f in self.search_fields if f != 'price']
        
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        self.search_fields = original_search_fields
        
        if search_term:
            from django.db.models import Q, CharField
            from django.db.models.functions import Cast
            
            clean_term = search_term.replace('.', '').replace(',', '')
            if clean_term.isdigit() or search_term.strip():
                qs_price = self.model.objects.annotate(
                    price_str=Cast('price', CharField())
                ).filter(price_str__icontains=clean_term)
                queryset = queryset | qs_price
                
        return queryset, use_distinct

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

from services_menu.models import CatalogDiscount

@admin.register(CatalogDiscount)
class CatalogDiscountAdmin(BaseRBACAdmin):
    list_display = ('code', 'description', 'discount_type', 'value', 'is_active')
    list_filter = ('discount_type', 'is_active')
    search_fields = ('code', 'description')
