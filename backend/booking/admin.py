from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404, render
from django.utils.safestring import mark_safe
from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline, StackedInline
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from .models import BookingDetail, Billing

from django import forms
from django.db.models import Max
from .models import MenuLink, SiteSettings, ClinicBranch, SocialLink

from .models import (
    Clinic, ServiceCategory, ServiceDetail, TimeSlot, Customer, Employee, 
    Booking, BookingStatusHistory, Payment, TopupInfo,
    InventoryDetail, InventoryUsage, Article, BookingDetail
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
from tinymce.widgets import TinyMCE

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
    list_display = ('name', 'hotline', 'address', 'total_chairs')
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
from django.utils.safestring import mark_safe
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
    search_fields = ('name','estimate_time')


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
    list_display = ('category','code', 'name', 'difficulty', 'formatted_price', 'warranty')
    list_filter = ['category', 'difficulty', PriceRangeFilter, 'warranty']
    search_fields = ['category__name', 'code', 'name', 'difficulty', 'price', 'warranty']
    import_template_name = 'admin/booking/servicedetail/import.html'
    ordering = ['category', 'code']

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
    list_display = ('start_time', 'end_time')

@admin.register(Customer)
class CustomerAdmin(BaseRBACAdmin):
    list_display = ('name', 'gender', 'phone', 'customer_dob', 'address', 'email')
    search_fields = ('name', 'phone', 'email', 'address')
    list_filter = ('address', 'gender')

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
from tinymce.widgets import TinyMCE

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
        widgets = {
            
        }

    def clean_actual_price(self):
        val = self.cleaned_data.get('actual_price')
        if val:
            # Xóa dấu phẩy nếu người dùng quên/chưa xử lý JS
            return int(str(val).replace(',', ''))
        return val

from django import forms
from tinymce.widgets import TinyMCE

class BookingDetailInlineForm(forms.ModelForm):
    class Meta:
        model = BookingDetail
        fields = '__all__'
        widgets = {
            
        }
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
    list_display = ('booking_id', 'customer', 'start_time', 'estimated_duration', 'notes')
    list_filter = ('clinic', 'status', 'estimated_duration')
    search_fields = ('customer__name', 'customer__phone', 'notes', 'estimated_duration')
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


from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

class CustomCloudinaryWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        
        # 1. Nếu có ảnh đã lưu: Hiện ảnh (click để phóng to) và Tên file
        if value and hasattr(value, 'url'):
            # Trích xuất tên file từ Cloudinary ID
            file_name = str(value).split('/')[-1] if value else 'Đã tải lên'
            
            output.append(f'''
                <div style="margin-bottom: 16px; padding: 12px; background: rgba(255,255,255,0.05); border-radius: 8px; border: 1px dashed #4b5563; width: fit-content;">
                    <a href="{value.url}" target="_blank" style="display: block; cursor: zoom-in; border-radius: 4px; overflow: hidden; margin-bottom: 8px; transition: opacity 0.2s;" onmouseover="this.style.opacity='0.8'" onmouseout="this.style.opacity='1'">
                        <img src="{value.url}" style="max-height: 200px; display: block;" title="Nhấn để phóng to ảnh" />
                    </a>
                    <div style="font-size: 13px; color: #9ca3af; display: flex; align-items: center; gap: 6px;">
                        <svg width="16" height="16" fill="currentColor" viewBox="0 0 20 20"><path d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z"></path></svg>
                        {file_name}
                    </div>
                </div>
            ''')
            
        # 2. Render input chọn file (thêm CSS class để đồng bộ theme Unfold)
        output.append(super().render(name, value, attrs, renderer))
        
        return mark_safe(''.join(output))

class ArticleAdminForm(forms.ModelForm):
    thumbnail = forms.FileField(
        widget=CustomCloudinaryWidget(),
        required=False,
        label="Ảnh Thumbnail (Tải lên)"
    )
    content = forms.CharField(
        widget=TinyMCE(attrs={'cols': 80, 'rows': 30}), 
        label="Nội dung",
        required=False
    )

    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
        }
        widgets = {
            
        }



    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'category' not in self.fields: return

        from .models import MenuLink
        mapping = {}
        parents = {}
        for child in MenuLink.objects.filter(parent__isnull=False).select_related('parent'):
            pid = str(child.parent_id)
            if pid not in mapping: 
                mapping[pid] = []
                parents[pid] = child.parent.title
            mapping[pid].append({'id': child.id, 'title': child.title})

        parent_options = '<option value="">-- Bước 1: Chọn Danh mục Cha --</option>'
        for pid, ptitle in parents.items():
            parent_options += f'<option value="{pid}">{ptitle}</option>'

        initial_parent = self.instance.category.parent_id if self.instance and hasattr(self.instance, 'category') and self.instance.category else ''

        js = f"""
        
        <style>
            /* Ép màu nền tối và chữ sáng cho các mục xổ xuống */
            #custom_parent_filter option, select[name="category"] option {{
                background-color: #1e293b !important;
                color: #f8fafc !important;
            }}
        
            /* Xóa mũi tên SVG trôi nổi */
            .field-category .pointer-events-none {{{{ display: none !important; }}}}
            /* Trả lại mũi tên mặc định */
            select[name="category"], #custom_parent_filter {{{{ appearance: auto !important; }}}}

</style>
        <div id="custom_parent_filter_wrapper" style="margin-bottom: 12px;">
            
            <select id="custom_parent_filter" style="width: 100%; padding: 0.5rem; border-radius: 0.375rem; border: 1px solid #374151; background-color: transparent; color: inherit; appearance: none;">
                {parent_options}
            </select>
        </div>
        <script>
        document.addEventListener("DOMContentLoaded", function() {{
            var mapping = {json.dumps(mapping)};
            var initialParent = "{initial_parent}";
            var filterDiv = document.getElementById("custom_parent_filter_wrapper");
            var parentSel = document.getElementById("custom_parent_filter");
            var childSel = document.querySelector('select[name="category"]');

            if (!parentSel || !childSel || !filterDiv) return;

            childSel.parentNode.insertBefore(filterDiv, childSel);
            // Ép ẩn cụm nút công cụ liên kết
            if (childSel.parentNode) {{
                var links = childSel.parentNode.querySelectorAll("a");
                links.forEach(function(l) {{ l.style.display = "none"; }});
            }}
    
            if (initialParent) parentSel.value = initialParent;

            function update() {{
                var pid = parentSel.value;
                var currentChildVal = childSel.value;
                childSel.innerHTML = '<option value="">-- Bước 2: Chọn Danh mục Con --</option>';
                if (pid && mapping[pid]) {{
                    mapping[pid].forEach(function(c) {{
                        var opt = document.createElement("option");
                        opt.value = c.id;
                        opt.textContent = c.title;
                        if (c.id == currentChildVal) opt.selected = true;
                        childSel.appendChild(opt);
                    }});
                }}
            }}

            parentSel.addEventListener("change", function() {{
                childSel.value = "";
                update();
            }});
            setTimeout(update, 50);
        }});
        </script>
        """
        self.fields['category'].help_text = mark_safe(js)


@admin.register(Article)


class ArticleAdmin(BaseRBACAdmin):
    form = ArticleAdminForm
    class Media:
        js = (
            'js/parse_docx.js',
            'js/preview_cloudinary.js',
            'tinymce/tinymce.min.js',
            'django_tinymce/init_tinymce.js',
        )
    def get_form(self, request, obj=None, **kwargs):
        css_style = """
<style>
    .field-thumbnail input[type="file"] {{
        color: transparent;
    }}
    .field-thumbnail input[type="file"]::-webkit-file-upload-button {{
        visibility: hidden;
    }}
    .field-thumbnail input[type="file"]::before {{
        content: 'Tải ảnh lên (Upload)';
        display: inline-block;
        background: #1e293b;
        color: white;
        border: 1px solid #999;
        border-radius: 6px;
        padding: 8px 16px;
        outline: none;
        white-space: nowrap;
        cursor: pointer;
        font-weight: 500;
        font-size: 14px;
    }}
    .field-thumbnail input[type="file"]:hover::before {{
        background: #334155;
    }}

            /* Xóa mũi tên SVG trôi nổi */
            .field-category .pointer-events-none {{{{ display: none !important; }}}}
            /* Trả lại mũi tên mặc định */
            select[name="category"], #custom_parent_filter {{{{ appearance: auto !important; }}}}

</style>
<script src="https://media-library.cloudinary.com/global/all.js"></script>
"""
        from django.utils.safestring import mark_safe
        form = super().get_form(request, obj, **kwargs)
        js_click_image = """
        <script>
            document.addEventListener("DOMContentLoaded", function() {
                setTimeout(function() {
                    let images = document.querySelectorAll('.form-row img');
                    images.forEach(function(img) {
                        img.style.cursor = 'zoom-in';
                        img.title = 'Click để xem kích thước đầy đủ';
                        img.addEventListener('click', function() {
                            window.open(img.src, '_blank');
                        });
                    });
                }, 1000);
            });
        </script>
        """

        js_click_image += """
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/cropperjs/1.5.13/cropper.min.js"></script>

<style>
    /* Giao diện Popup cắt ảnh */
    #cropModal {{ display: none; position: fixed; z-index: 9999; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.8); }}
    #cropContainer {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); background: #fff; padding: 20px; border-radius: 8px; max-width: 90%; max-height: 90%; text-align: center; }}
    #imageToCrop {{ max-width: 100%; max-height: 60vh; display: block; margin: 0 auto 15px auto; }}
    .crop-btn {{ padding: 10px 20px; margin: 5px; border: none; border-radius: 5px; cursor: pointer; font-weight: bold; }}
    .btn-confirm {{ background-color: #2563eb; color: white; }}
    .btn-cancel {{ background-color: #ef4444; color: white; }}
    #cropPreview {{ display: none; margin-top: 15px; max-width: 250px; border-radius: 8px; border: 2px dashed #2563eb; }}

            /* Xóa mũi tên SVG trôi nổi */
            .field-category .pointer-events-none {{{{ display: none !important; }}}}
            /* Trả lại mũi tên mặc định */
            select[name="category"], #custom_parent_filter {{{{ appearance: auto !important; }}}}

</style>

<div id="cropModal">
    <div id="cropContainer">
        <img id="imageToCrop" src="" alt="Ảnh gốc">
        <button type="button" class="crop-btn btn-cancel" id="btnCancelCrop">Hủy bỏ</button>
        <button type="button" class="crop-btn btn-confirm" id="btnConfirmCrop">Cắt & Xác nhận</button>
    </div>
</div>

<script>
document.addEventListener("DOMContentLoaded", function() {
    let fileInput = document.querySelector('.field-thumbnail input[type="file"]') || document.querySelector('input[name="thumbnail"]');
    if (!fileInput) return;

    let container = fileInput.parentNode;
    let previewImg = document.createElement('img');
    previewImg.id = "cropPreview";
    container.appendChild(previewImg);

    let cropper;
    let modal = document.getElementById('cropModal');
    let imageToCrop = document.getElementById('imageToCrop');

    // Mở popup ngay khi chọn file
    fileInput.addEventListener('change', function(e) {
        let files = e.target.files;
        if (files && files.length > 0) {
            let reader = new FileReader();
            reader.onload = function(event) {
                imageToCrop.src = event.target.result;
                modal.style.display = 'block';
                
                if (cropper) cropper.destroy();
                cropper = new Cropper(imageToCrop, {
                    aspectRatio: 1.5, // Giữ nguyên tỷ lệ 3:2 của thẻ Blog
                    viewMode: 2,
                    autoCropArea: 1
                });
            };
            reader.readAsDataURL(files[0]);
        }
    });

    // Nút Hủy
    document.getElementById('btnCancelCrop').addEventListener('click', function() {
        modal.style.display = 'none';
        if (cropper) cropper.destroy();
        fileInput.value = ""; // Xóa file đã chọn
    });

    // Nút Xác nhận cắt
    document.getElementById('btnConfirmCrop').addEventListener('click', function() {
        if (!cropper) return;
        cropper.getCroppedCanvas({ width: 900, height: 600 }).toBlob(function(blob) {
            // Thay thế file gốc bằng file đã cắt
            let dt = new DataTransfer();
            let croppedFile = new File([blob], "thumbnail_cropped.jpg", { type: "image/jpeg" });
            dt.items.add(croppedFile);
            fileInput.files = dt.files; // Gán lại vào input gốc của Django

            // Hiển thị ảnh xem trước
            let croppedUrl = URL.createObjectURL(blob);
            previewImg.src = croppedUrl;
            previewImg.style.display = 'block';

            // Tắt popup
            modal.style.display = 'none';
            cropper.destroy();
        }, 'image/jpeg', 0.9);
    });
});
</script>
"""
        if 'title' in form.base_fields:
            if not form.base_fields['title'].help_text:
                form.base_fields['title'].help_text = ''
            form.base_fields['title'].help_text += mark_safe(js_click_image)

        return form


    list_display = ('title', 'category', 'slug', 'user', 'created_on')
    search_fields = ('title', 'slug')
    list_filter = ('created_on',)
    prepopulated_fields = {'slug': ('title',)}
    
    exclude = ('user_id', 'user', 'created_on')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.user = request.user
            obj.created_on = timezone.now()
        super().save_model(request, obj, form, change)


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

@admin.register(BookingDetail)
class BookingDetailAdmin(BaseRBACAdmin):
    list_display = ('booking', 'service_detail')
    search_fields = ('booking__booking_id', 'service_detail__name')
class MenuLinkInline(TabularInline):
    model = MenuLink
    fk_name = 'parent'
    extra = 0
    ordering_field = 'order'
    hide_ordering_field = True
    fields = ('title', 'url', 'is_active')
    verbose_name = "Menu con"
    verbose_name_plural = "Danh sách Menu con"

@admin.register(MenuLink)
class MenuLinkAdmin(ModelAdmin):
    list_display = ('title', 'url', 'order', 'is_active')
    search_fields = ('title',)
    inlines = [MenuLinkInline]
    exclude = ('parent',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(parent__isnull=True)

class ClinicBranchInline(TabularInline):
    model = ClinicBranch
    extra = 0
    ordering_field = 'order'
    hide_ordering_field = True

class SocialLinkInline(TabularInline):
    model = SocialLink
    extra = 0
    ordering_field = 'order'
    hide_ordering_field = True

class SiteSettingsAdminForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        js_script = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            if (typeof django !== 'undefined' && django.jQuery) {
                django.jQuery(document).on('formset:added', function(event, $row, formsetName) {
                    var $orderInput = $row.find('input[name$="-order"]');
                    if ($orderInput.length) {
                        var maxOrder = -1;
                        django.jQuery('input[name^="' + formsetName + '-"][name$="-order"]').not($orderInput).each(function() {
                            var val = parseInt(django.jQuery(this).val(), 10);
                            if (!isNaN(val) && val > maxOrder) {
                                maxOrder = val;
                            }
                        });
                        $orderInput.val(maxOrder + 1);
                    }
                });
            }
        });
        </script>
        """
        if 'email' in self.fields:
            self.fields['email'].help_text = mark_safe((self.fields['email'].help_text or '') + js_script)

@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    form = SiteSettingsAdminForm
    inlines = [ClinicBranchInline, SocialLinkInline]
    list_display = ('__str__', 'email')
    
    fieldsets = (
        ("Thông tin liên hệ chính", {
            "fields": ("email", "working_hours")
        }),
        ("Cài đặt Tiêu đề Footer", {
            "fields": ("branch_section_title", "social_section_title"),
            "description": "Các tiêu đề này sẽ hiển thị ngay phía trên danh sách Cơ sở và Mạng xã hội tương ứng."
        }),
    )

    def changelist_view(self, request, extra_context=None):
        obj = self.model.objects.first()
        if obj:
            url = reverse('admin:%s_%s_change' % (self.model._meta.app_label, self.model._meta.model_name), args=[obj.id])
            return redirect(url)
        return super().changelist_view(request, extra_context)

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for instance in instances:
            if getattr(instance, 'pk', None) is None and getattr(instance, 'order', None) == 0:
                model_class = type(instance)
                max_order = model_class.objects.filter(settings=instance.settings).aggregate(Max('order'))['order__max'] or 0
                instance.order = max_order + 1
            instance.save()
        formset.save_m2m()
