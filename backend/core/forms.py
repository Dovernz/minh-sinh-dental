from django import forms
from django.contrib.auth.models import Group, Permission
from django.contrib.admin.widgets import FilteredSelectMultiple

# Ánh xạ thủ công, lấy model name làm key, tên Menu mong muốn làm value
PERMISSION_GROUP_MAPPING = {
    # Quản lý Booking
    'dailyschedule': 'Quản lý Booking',
    'weeklyschedule': 'Quản lý Booking',
    'managebooking': 'Quản lý Booking',
    
    # Giao dịch
    'bookingbill': 'Giao dịch',
    'billing': 'Giao dịch',
    
    # Khách hàng & Dịch vụ
    'customer': 'Khách hàng & Dịch vụ',
    'clinic': 'Khách hàng & Dịch vụ',
    'servicecategory': 'Khách hàng & Dịch vụ',
    'servicedetail': 'Khách hàng & Dịch vụ',
    'timeslot': 'Khách hàng & Dịch vụ',
    'servicecategoryproxy': 'Khách hàng & Dịch vụ',
    'servicedetailproxy': 'Khách hàng & Dịch vụ',
    'catalogservicedetail': 'Khách hàng & Dịch vụ',
    'catalogdiscount': 'Khách hàng & Dịch vụ',
    
    # Tài chính & Vật tư
    'payment': 'Tài chính & Vật tư',
    'inventorydetail': 'Tài chính & Vật tư',
    'inventoryusage': 'Tài chính & Vật tư',
    'discount': 'Tài chính & Vật tư',
    'topupinfo': 'Tài chính & Vật tư',
    
    # Hệ thống & Quản trị User
    'user': 'Hệ thống & Quản trị User',
    'group': 'Hệ thống & Quản trị User',
    'employee': 'Hệ thống & Quản trị User',
    
    # Marketing
    'marketingarticle': 'Marketing',
    'article': 'Marketing',
    
    # Các model còn lại sẽ mặc định gom vào nhóm 'Database'
}

def get_dynamic_permission_mapping():
    """Tự động quét cấu hình UNFOLD SIDEBAR để tạo từ điển mapping"""
    from django.conf import settings
    from django.urls import resolve
    mapping = {}
    sidebar = getattr(settings, 'UNFOLD', {}).get('SIDEBAR', {})
    
    # Xử lý an toàn cấu trúc SIDEBAR có thể là dict hoặc list
    if isinstance(sidebar, dict):
        sidebar = sidebar.get('navigation', [])
        
    for group in sidebar:
        group_title = group.get('title', 'Khác')
        for item in group.get('items', []):
            try:
                url_path = str(item.get('link', ''))
                if not url_path: continue
                match = resolve(url_path)
                view_name = match.view_name
                if view_name.startswith('admin:') and view_name.endswith('_changelist'):
                    core_name = view_name.replace('admin:', '').replace('_changelist', '')
                    *app_parts, model_name = core_name.rsplit('_', 1)
                    if model_name:
                        mapping[model_name] = group_title
            except Exception:
                continue
    return mapping

class CustomPermissionSelectMultiple(FilteredSelectMultiple):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Nạp từ điển tự động quét
        self.dynamic_mapping = get_dynamic_permission_mapping()

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        option = super().create_option(name, value, label, selected, index, subindex, attrs)
        if value:
            try:
                # VÁ LỖI: Trích xuất ID linh hoạt. Hỗ trợ cả primitive type (int/str) và ModelChoiceIteratorValue
                perm_id = getattr(value, 'value', value)
                
                # Lấy object permission
                perm = Permission.objects.get(pk=perm_id)
                model_name = perm.content_type.model
                
                # Lớp 1: Khai báo tĩnh
                if model_name in PERMISSION_GROUP_MAPPING:
                    new_group_name = PERMISSION_GROUP_MAPPING[model_name]
                # Lớp 2: Quét động
                elif model_name in getattr(self, 'dynamic_mapping', {}):
                    new_group_name = self.dynamic_mapping[model_name]
                # Lớp 3: Mặc định
                else:
                    new_group_name = 'Database'
                
                # Ghi đè nhãn mới
                option['label'] = f"{new_group_name} | {perm.content_type.name} | {perm.name}"
            except Exception as e:
                # In lỗi ra console server để dễ dàng debug nếu còn lỗi
                print(f"[Custom Widget Error] Không thể xử lý value {value}: {e}")
                pass
        return option

    def optgroups(self, name, value, attrs=None):
        groups = super().optgroups(name, value, attrs)
        for group in groups:
            group_name, options, index = group
            options.sort(key=lambda opt: opt['label'])
        return groups

class CustomGroupAdminForm(forms.ModelForm):
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=CustomPermissionSelectMultiple('permissions', False),
        required=False,
    )
    class Meta:
        model = Group
        fields = '__all__'
