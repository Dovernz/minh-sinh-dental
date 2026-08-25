
from django.shortcuts import get_object_or_404, render
from django.utils.html import format_html
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import BookingDetail, Billing
from .models import (
    Clinic, ServiceCategory, ServiceDetail, TimeSlot, Customer, Employee, 
    Booking, BookingStatusHistory, Payment, TopupInfo,
    InventoryDetail, InventoryUsage, Article
)


admin.site.unregister(User)
admin.site.unregister(Group)

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Admin').exists()

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        return request.user.groups.filter(name='Admin').exists()

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        new_fieldsets = []
        for name, opts in fieldsets:
            fields = list(opts.get('fields', []))
            if 'last_login' in fields: fields.remove('last_login')
            if 'date_joined' in fields: fields.remove('date_joined')
            
            # Chặn nhóm Admin tự ý cấp quyền is_superuser
            if not request.user.is_superuser and 'is_superuser' in fields:
                fields.remove('is_superuser')
                
            if fields:
                new_fieldsets.append((name, {**opts, 'fields': tuple(fields)}))
        return tuple(new_fieldsets)

def is_staff(request):
    return request.user.groups.filter(name='Staff').exists() and not request.user.is_superuser and not request.user.groups.filter(name='Admin').exists()

class BaseRBACAdmin(ModelAdmin):
    def has_module_permission(self, request):
        if request.user.is_superuser:
            return True
        if request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False

    def has_view_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False


    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('import-template/', self.admin_site.admin_view(self.download_template), name='import_template_servicedetail'),
        ]
        return my_urls + urls

    def download_template(self, request):
        from django.http import HttpResponse
        resource = ServiceDetailResource()
        dataset = resource.export(queryset=self.model.objects.none())
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Template_DichVu.xlsx"'
        return response

    def has_add_permission(self, request):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False
        
    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser or request.user.groups.filter(name__in=['Reception', 'Admin']).exists():
            return True
        return False

import urllib.request
import json
from django.core.cache import cache
from django import forms

def get_vietqr_banks():
    choices = cache.get('vietqr_bank_choices')
    if choices is None:
        try:
            req = urllib.request.Request('https://api.vietqr.io/v2/banks', headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8')).get('data', [])
                    choices = [(str(bank['bin']), f"{bank['shortName']} - {bank['name']}") for bank in data]
                    cache.set('vietqr_bank_choices', choices, 86400)
                else:
                    choices = [('', 'L?i t?i danh s?ch ng?n h?ng')]
        except Exception as e:
            choices = [('', 'Kh?ng th? k?t n?i VietQR')]
    return choices

class TopupInfoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['bank_name'].widget = forms.Select(choices=get_vietqr_banks())
        
@admin.register(TopupInfo)
class TopupInfoAdmin(BaseRBACAdmin):
    list_display = ('bank_name', 'account_number', 'account_name', 'is_default')
    list_filter = ('is_default',)
    form = TopupInfoForm

@admin.register(Clinic)
class ClinicAdmin(BaseRBACAdmin):
    list_display = ('name', 'hotline', 'created_on')
    search_fields = ('name', 'hotline', 'address')
    list_filter = ('created_on',)

from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export import resources, fields
from import_export.widgets import ForeignKeyWidget
from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin
from import_export.formats.base_formats import XLSX, CSV
from django.urls import path
from django.shortcuts import get_object_or_404, render
from django.utils.html import format_html
from django.http import HttpResponse

class ServiceCategoryResource(resources.ModelResource):
    class Meta:
        model = ServiceCategory
        exclude = ('created_on',)
        import_id_fields = ('name',)

class ServiceDetailResource(resources.ModelResource):
    category = fields.Field(column_name='category', attribute='category', widget=ForeignKeyWidget(ServiceCategory, 'name'))

    class Meta:
        model = ServiceDetail
        exclude = ('created_on',)
        import_id_fields = ('category', 'code', 'name')

    def before_import_row(self, row, **kwargs):
        code_val = row.get('code')
        if not code_val or str(code_val).strip() == '' or str(code_val).lower() == 'nan':
            row['code'] = None

        # Validate Price
        price = row.get('price')
        if price is not None and str(price).strip():
            try:
                price_str = str(price).replace(',', '').replace('.', '').strip()
                row['price'] = int(price_str)
            except ValueError:
                raise ValueError(f"Lỗi ở cột Giá tiền: '{price}' không phải là số hợp lệ. Vui lòng chỉ nhập số.")
        
        # Validate Difficulty
        diff = row.get('difficulty')
        if diff:
            valid_difficulties = [c[0] for c in ServiceDetail.DIFFICULTY_CHOICES]
            if diff not in valid_difficulties:
                raise ValueError(f"Lỗi ở cột Độ khó: '{diff}' không hợp lệ. Vui lòng chọn một trong: {', '.join(valid_difficulties)}.")

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(ImportExportActionModelAdmin, BaseRBACAdmin):
    resource_classes = [ServiceCategoryResource]
    list_display = ('name', 'estimate_time', 'created_on')
    search_fields = ('name',)


    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('import-template/', self.admin_site.admin_view(self.download_template), name='import_template_servicedetail'),
        ]
        return my_urls + urls

    def download_template(self, request):
        from django.http import HttpResponse
        resource = ServiceDetailResource()
        dataset = resource.export(queryset=self.model.objects.none())
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Template_DichVu.xlsx"'
        return response

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated

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

@admin.register(ServiceDetail)
class ServiceDetailAdmin(ImportExportActionModelAdmin, BaseRBACAdmin):
    resource_classes = [ServiceDetailResource]
    formats = [XLSX, CSV]
    list_display = ('code', 'name', 'difficulty', 'formatted_price', 'category')
    list_filter = ['category', 'difficulty', PriceRangeFilter]
    search_fields = ['category__name', 'code', 'name', 'difficulty', 'price', 'warranty']
    import_template_name = 'admin/booking/servicedetail/import.html'

    def formatted_price(self, obj):
        if obj.price is not None:
            return "{:,.0f}".format(obj.price)
        return "-"
    formatted_price.short_description = 'Giá'

    def get_export_queryset(self, request):
        qs = super().get_export_queryset(request)
        if request.GET.get('template') == '1':
            return qs.none()
        return qs


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


    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('import-template/', self.admin_site.admin_view(self.download_template), name='import_template_servicedetail'),
        ]
        return my_urls + urls

    def download_template(self, request):
        from django.http import HttpResponse
        resource = ServiceDetailResource()
        dataset = resource.export(queryset=self.model.objects.none())
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Template_DichVu.xlsx"'
        return response

    def has_add_permission(self, request):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser or request.user.groups.filter(name__in=['Admin', 'Accountant']).exists()
    def has_view_permission(self, request, obj=None):
        return request.user.is_authenticated


@admin.register(TimeSlot)
class TimeSlotAdmin(BaseRBACAdmin):
    list_display = ('start_time', 'end_time', 'created_on')

@admin.register(Customer)
class CustomerAdmin(BaseRBACAdmin):
    list_display = ('name', 'phone', 'customer_dob', 'email', 'created_on')
    search_fields = ('name', 'phone', 'email')
    list_filter = ('created_on',)

@admin.register(Employee)
class EmployeeAdmin(BaseRBACAdmin):
    exclude = ('user',)
    list_display = ('full_name', 'phone', 'specialty', 'role', 'created_on')
    list_filter = ('specialty', 'role')
    search_fields = ('full_name', 'phone', 'email')

    def save_model(self, request, obj, form, change):
        if obj.role == 'Admin' and not request.user.is_superuser:
            raise PermissionDenied('Chỉ Superuser mới được tạo Admin')
            
        if not change:
            username = obj.phone or obj.email or f"user_{obj.employee_id}"
            new_user = User.objects.create_user(username=username, password='password123')
            obj.user = new_user
            
        if obj.user and obj.role:
            group = Group.objects.get(name=obj.role)
            obj.user.groups.clear()
            obj.user.groups.add(group)
            obj.user.is_staff = True
            obj.user.save()
            
        super().save_model(request, obj, form, change)

from django import forms

class BookingAdminForm(forms.ModelForm):
    custom_service_code = forms.ChoiceField(
        label='Mã dịch vụ (Tùy chỉnh)', 
        required=False,
        choices=[('', '---------')]
    )
    custom_difficulty = forms.CharField(
        label='Độ khó', 
        required=False,
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )
    actual_price = forms.CharField(
        label='Số tiền thực tế',
        required=False,
        widget=forms.TextInput(attrs={'class': 'formatted-price'})
    )

    class Meta:
        model = Booking
        fields = '__all__'

    def clean_actual_price(self):
        val = self.cleaned_data.get('actual_price')
        if val:
            # Xóa dấu phẩy nếu người dùng quên/chưa xử lý JS
            return int(str(val).replace(',', ''))
        return val

from django import forms

class BookingDetailInlineForm(forms.ModelForm):
    class Meta:
        model = BookingDetail
        fields = '__all__'
        widgets = {
            'actual_price': forms.TextInput(attrs={'class': 'formatted-price', 'type': 'text'}),
        }

class BookingDetailInline(TabularInline):
    model = BookingDetail
    form = BookingDetailInlineForm
    extra = 1
    fields = ('service_detail', 'doctor', 'actual_price')

@admin.register(Booking)
class BookingAdmin(BaseRBACAdmin):
    inlines = [BookingDetailInline]
    form = BookingAdminForm
    list_display = ('booking_id', 'customer', 'start_time', 'status')
    list_filter = ('clinic', 'status')
    search_fields = ('customer__name', 'customer__phone', 'notes')
    # readonly_fields = ('category',) # Bỏ để kích hoạt AJAX

    class Media:
        js = ('admin/js/booking_chained_select.js',)

    def save_model(self, request, obj, form, change):
        if not obj.actual_price and obj.service_detail:
            obj.actual_price = obj.service_detail.price
        super().save_model(request, obj, form, change)

@admin.register(BookingStatusHistory)
class BookingStatusHistoryAdmin(BaseRBACAdmin):
    list_display = ('booking', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('booking__customer__name',)
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(Payment)
class PaymentAdmin(BaseRBACAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'created_at')
    list_filter = ('payment_method', 'created_at')
    search_fields = ('booking__customer__name',)



@admin.register(InventoryDetail)
class InventoryDetailAdmin(BaseRBACAdmin):
    list_display = ('item_name', 'unit', 'category', 'price_per_unit')
    list_filter = ('category',)
    search_fields = ('item_name',)

@admin.register(InventoryUsage)
class InventoryUsageAdmin(BaseRBACAdmin):
    list_display = ('booking', 'item', 'quantity_used', 'employee', 'created_on')
    list_filter = ('created_on',)
    search_fields = ('booking__customer__name', 'item__item_name', 'employee__full_name')

@admin.register(Article)
class ArticleAdmin(BaseRBACAdmin):
    list_display = ('title', 'slug', 'user', 'created_on')
    search_fields = ('title', 'slug')
    list_filter = ('created_on',)
    prepopulated_fields = {'slug': ('title',)}


from booking.models import Billing, TopupInfo
from django.utils.safestring import mark_safe

@admin.register(Billing)
class BillingAdmin(BaseRBACAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    list_display = ('booking', 'sub_total', 'discount', 'final_total', 'created_on', 'print_invoice_button')
    readonly_fields = ('sub_total', 'adjustment', 'final_total', 'payment_qr_code', 'print_invoice_button')
    search_fields = ('booking__booking_id', 'booking__customer__name')
    
    fieldsets = (
        ('Thông tin chung', {
            'fields': ('booking',)
        }),
        ('Kế toán', {
            'fields': ('sub_total', 'discount', 'adjustment', 'final_total')
        }),
        ('Thanh toán', {
            'fields': ('payment_qr_code', 'print_invoice_button')
        })
    )


    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('<int:billing_id>/print/', self.admin_site.admin_view(self.print_invoice_view), name='billing-print-invoice'),
        ]
        return my_urls + urls

    def print_invoice_view(self, request, billing_id):
        from .models import TopupInfo
        billing = get_object_or_404(Billing, pk=billing_id)
        booking = billing.booking
        details = booking.details.all()
        customer = booking.customer
        
        qr_url = ""
        if billing.final_total > 0:
            topup = TopupInfo.objects.filter(is_default=True).first()
            if not topup:
                topup = TopupInfo.objects.first()
            if topup:
                bank = topup.bank_name
                account = topup.account_number
                name = topup.account_name.replace(' ', '%20') if topup.account_name else ''
                amount = int(billing.final_total)
                info = f"Thanh toan Booking {booking.booking_id}".replace(' ', '%20')
                qr_url = f"https://img.vietqr.io/image/{bank}-{account}-compact2.png?amount={amount}&addInfo={info}&accountName={name}"

        context = {
            'billing': billing,
            'booking': booking,
            'details': details,
            'customer': customer,
            'qr_url': qr_url,
        }
        return render(request, 'admin/booking/billing/invoice.html', context)

    def print_invoice_button(self, obj):
        if obj.pk:
            return format_html('<a href="{}/print/" target="_blank" class="button" style="background-color:#007bff; color:white; padding:5px 10px; border-radius:3px; text-decoration:none;">🖨️ In Hóa Đơn</a>', obj.pk)
        return ""
    print_invoice_button.short_description = "In Hóa Đơn"


    def payment_qr_code(self, obj):
        if obj.pk and obj.final_total > 0:
            topup = TopupInfo.objects.filter(is_default=True).first()
            if not topup:
                topup = TopupInfo.objects.first()
            if topup:
                # VietQR formula
                bank = topup.bank_name
                account = topup.account_number
                name = topup.account_name.replace(' ', '%20') if topup.account_name else ''
                amount = int(obj.final_total)
                info = f"Thanh toan Booking {obj.booking.booking_id}".replace(' ', '%20')
                url = f"https://img.vietqr.io/image/{bank}-{account}-compact2.png?amount={amount}&addInfo={info}&accountName={name}"
                return mark_safe(f'<img src="{url}" alt="QR Code" style="max-width: 300px;"/>')
        return "Chưa có thông tin hoặc tổng tiền = 0"
    payment_qr_code.short_description = "QR Thanh Toán"
