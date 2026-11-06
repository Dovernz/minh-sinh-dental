import json
from django import forms
from django.contrib.auth.models import Permission, Group
from django.utils.safestring import mark_safe

MENU_SECTIONS_DEFINITION = [
    {
        "id": "sec_booking",
        "short_title": "1. Booking",
        "title": "1. Quản lý Booking",
        "desc": "Các quyền liên quan đến xem lịch, đặt lịch khám và điều phối ghế điều trị",
        "permissions": [
            ("booking.view_booking", "Xem danh sách và chi tiết lịch hẹn bệnh nhân"),
            ("booking.add_booking", "Tạo mới lịch hẹn khám bệnh (Đặt lịch Tổng đài)"),
            ("booking.change_booking", "Chỉnh sửa trạng thái hoặc thời gian lịch hẹn"),
            ("booking.delete_booking", "Hủy / Xóa lịch hẹn khám"),
            ("operations.view_dailyschedule", "Xem giao diện Lịch Ngày điều phối ghế"),
            ("operations.view_weeklyschedule", "Xem giao diện Lịch Tuần điều phối ghế"),
            ("operations.view_managebooking", "Xem bảng quản lý điều hành Bookings"),
        ],
    },
    {
        "id": "sec_transaction",
        "short_title": "2. Giao dịch",
        "title": "2. Giao dịch & Thu ngân",
        "desc": "Các quyền thanh toán viện phí, thu ngân POS và quản lý công nợ",
        "permissions": [
            ("booking.add_payment", "Thu ngân và tạo phiếu thanh toán POS"),
            ("booking.view_payment", "Xem lịch sử thanh toán và danh sách hóa đơn"),
            ("booking.change_payment", "Điều chỉnh thanh toán & Thu hồi công nợ bệnh nhân"),
            ("booking.view_bookingbill", "Xem phiếu thanh toán tổng hợp viện phí"),
            ("booking.add_bookingbill", "Tạo phiếu thanh toán tổng hợp viện phí"),
        ],
    },
    {
        "id": "sec_customer_service",
        "short_title": "3. Khách hàng",
        "title": "3. Khách hàng & Dịch vụ",
        "desc": "Các quyền quản lý hồ sơ bệnh nhân, cơ sở phòng khám và bảng giá dịch vụ",
        "permissions": [
            ("booking.view_customer", "Xem hồ sơ thông tin bệnh nhân"),
            ("booking.add_customer", "Tiếp nhận & Tạo mới hồ sơ bệnh nhân"),
            ("booking.change_customer", "Cập nhật bệnh án và thông tin liên hệ bệnh nhân"),
            ("booking.delete_customer", "Xóa hồ sơ bệnh nhân"),
            ("booking.view_clinic", "Xem danh sách cơ sở phòng khám"),
            ("booking.add_clinic", "Thêm mới cơ sở phòng khám"),
            ("booking.change_clinic", "Cập nhật thông tin cơ sở phòng khám"),
            ("booking.view_servicecategory", "Xem danh mục nhóm dịch vụ điều trị"),
            ("booking.add_servicecategory", "Thêm mới danh mục nhóm dịch vụ"),
            ("booking.change_servicecategory", "Chỉnh sửa danh mục nhóm dịch vụ"),
            ("booking.view_servicedetail", "Xem chi tiết bảng giá dịch vụ điều trị"),
            ("booking.add_servicedetail", "Thêm mới dịch vụ kỹ thuật và định giá"),
            ("booking.change_servicedetail", "Cập nhật đơn giá và thời lượng dịch vụ"),
            ("booking.view_timeslot", "Xem cấu hình khung giờ khám"),
            ("booking.change_timeslot", "Cập nhật khung giờ làm việc của phòng khám"),
            ("booking.view_catalogdiscount", "Xem chương trình khuyến mãi & giảm giá"),
        ],
    },
    {
        "id": "sec_finance_inventory",
        "short_title": "4. Tài chính",
        "title": "4. Tài chính & Kho vật tư",
        "desc": "Các quyền xem hoa hồng Bác sĩ, cấu hình nạp tiền, quản lý kho và tiêu hao",
        "permissions": [
            ("booking.view_commissionrate", "Xem tỷ lệ hoa hồng điều trị của Bác sĩ"),
            ("booking.change_commissionrate", "Cập nhật định mức hoa hồng Bác sĩ"),
            ("booking.view_topupinfo", "Xem cấu hình tài khoản nạp tiền và cổng thanh toán"),
            ("booking.change_topupinfo", "Cập nhật thông tin tài khoản ngân hàng nhận tiền"),
            ("booking.view_inventorydetail", "Xem tồn kho vật tư và thiết bị nha khoa"),
            ("booking.add_inventorydetail", "Nhập kho vật tư y tế mới"),
            ("booking.change_inventorydetail", "Điều chỉnh thông tin và số lượng kho vật tư"),
            ("booking.view_inventoryusage", "Xem lịch sử tiêu hao vật tư điều trị"),
            ("booking.add_inventoryusage", "Ghi nhận tiêu hao vật tư cho ca điều trị"),
        ],
    },
    {
        "id": "sec_wordpress",
        "short_title": "5. Bài viết",
        "title": "5. Bài viết & Blog (WordPress)",
        "desc": "Quyền đăng nhập 1 chạm SSO và toàn quyền biên tập bài viết trên hệ thống WordPress CMS",
        "permissions": [
            ("booking.manage_wordpress_posts", "Toàn quyền quản lý & Viết bài trên WordPress (Kích hoạt SSO 1 chạm)"),
            ("booking.view_article", "Xem danh mục bài viết truyền thông"),
            ("booking.add_article", "Soạn thảo và xuất bản bài viết chuyên khoa mới"),
            ("booking.change_article", "Chỉnh sửa nội dung và thư viện ảnh bài viết"),
            ("booking.delete_article", "Gỡ bỏ / Xóa bài viết"),
        ],
    },
    {
        "id": "sec_web_config",
        "short_title": "6. Cấu hình Web",
        "title": "6. Cấu hình Website",
        "desc": "Các quyền tùy biến thanh điều hướng Header và thông tin nhận diện Footer",
        "permissions": [
            ("booking.view_menulink", "Xem cấu hình menu Header website"),
            ("booking.add_menulink", "Thêm liên kết điều hướng trên Header"),
            ("booking.change_menulink", "Chỉnh sửa liên kết điều hướng Header"),
            ("booking.view_sitesettings", "Xem thông tin thương hiệu và Footer website"),
            ("booking.change_sitesettings", "Cập nhật địa chỉ, hotline, giờ làm việc trên Footer"),
        ],
    },
    {
        "id": "sec_system_user",
        "short_title": "7. Hệ thống",
        "title": "7. Hệ thống & Quản trị User",
        "desc": "Các quyền quản trị tài khoản người dùng, phân quyền nhóm và hồ sơ nhân viên",
        "permissions": [
            ("auth.view_user", "Xem danh sách tài khoản người dùng"),
            ("auth.add_user", "Tạo tài khoản người dùng mới"),
            ("auth.change_user", "Phân quyền và cập nhật tài khoản người dùng"),
            ("auth.delete_user", "Khóa / Xóa tài khoản người dùng"),
            ("auth.view_group", "Xem danh sách nhóm vai trò phân quyền"),
            ("auth.add_group", "Tạo nhóm vai trò phân quyền mới"),
            ("auth.change_group", "Cấu hình phân quyền chi tiết cho nhóm"),
            ("booking.view_employee", "Xem danh sách hồ sơ Bác sĩ & Nhân viên"),
            ("booking.add_employee", "Thêm mới hồ sơ Bác sĩ & Nhân viên"),
            ("booking.change_employee", "Cập nhật phòng ban, chuyên khoa và chức vụ nhân sự"),
        ],
    },
]

# ------------------------------------------------------------------------------
# 1. WIDGET CHỌN NHÓM USER GỌN GÀNG (COMPACT GROUP SELECTOR)
# ------------------------------------------------------------------------------
class CompactGroupSelectWidget(forms.SelectMultiple):
    """
    Widget hiển thị danh sách các nhóm vai trò dưới dạng Pills/Tags chọn nhanh.
    Thay thế widget 2 ô cồng kềnh mặc định của Django.
    """
    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        elif not isinstance(value, (list, tuple)):
            value = [value]
        selected_ids = set(str(v) for v in value)

        all_groups = Group.objects.all().order_by('name')
        widget_id = attrs.get('id', f'id_{name}')

        html = []
        html.append(f'<div class="compact-group-selector" id="{widget_id}_container" style="width: 100%; margin-top: 4px;">')
        html.append('''
        <style>
            .field-groups {
                display: flex !important;
                flex-direction: column !important;
                align-items: stretch !important;
                width: 100% !important;
            }
            .field-groups > div:first-child {
                min-width: 100% !important;
                width: 100% !important;
                max-width: 100% !important;
                height: auto !important;
                display: block !important;
                margin-bottom: 8px !important;
            }
            .field-groups > div:first-child label {
                width: 100% !important;
                display: block !important;
                font-size: 13px !important;
                font-weight: 700 !important;
                color: #334155 !important;
                text-transform: uppercase;
                letter-spacing: 0.025em;
            }
            .dark .field-groups > div:first-child label {
                color: #94a3b8 !important;
            }
            .field-groups > .grow {
                width: 100% !important;
                flex-grow: 1 !important;
            }
            .compact-group-selector {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                align-items: center;
                padding: 10px 14px;
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            .dark .compact-group-selector {
                background: #0f172a;
                border-color: #334155;
            }
            .group-pill {
                display: inline-flex;
                align-items: center;
                gap: 6px;
                padding: 6px 14px;
                border-radius: 20px;
                border: 1px solid #cbd5e1;
                background: #ffffff;
                color: #334155;
                font-size: 13px;
                font-weight: 500;
                cursor: pointer;
                user-select: none;
                transition: all 0.15s ease;
            }
            .group-pill:hover {
                border-color: #94a3b8;
                background: #f1f5f9;
            }
            .dark .group-pill {
                background: #1e293b;
                border-color: #475569;
                color: #cbd5e1;
            }
            .dark .group-pill:hover {
                background: #334155;
                color: #ffffff;
            }
            .group-pill.selected {
                background: #2563eb !important;
                border-color: #1d4ed8 !important;
                color: #ffffff !important;
                font-weight: 600;
                box-shadow: 0 2px 4px rgba(37,99,235,0.25);
            }
            .group-pill-icon {
                font-size: 11px;
                font-weight: 700;
                display: inline-block;
                width: 14px;
                height: 14px;
                line-height: 14px;
                text-align: center;
                border-radius: 50%;
                background: rgba(0,0,0,0.1);
            }
            .group-pill.selected .group-pill-icon {
                background: rgba(255,255,255,0.25);
            }
            .group-actions-bar {
                margin-left: auto;
                display: flex;
                gap: 6px;
            }
            .btn-group-action {
                font-size: 11px;
                padding: 4px 8px;
                border-radius: 4px;
                background: transparent;
                border: 1px solid #cbd5e1;
                color: #64748b;
                cursor: pointer;
            }
            .btn-group-action:hover {
                background: #e2e8f0;
                color: #0f172a;
            }
            .dark .btn-group-action {
                border-color: #475569;
                color: #94a3b8;
            }
            .dark .btn-group-action:hover {
                background: #334155;
                color: #ffffff;
            }
        </style>
        ''')

        # Hidden Multi-Select thực tế
        html.append(f'<select name="{name}" id="{widget_id}" multiple style="display: none;">')
        for g in all_groups:
            is_sel = 'selected' if str(g.id) in selected_ids else ''
            html.append(f'<option value="{g.id}" {is_sel}>{g.name}</option>')
        html.append('</select>')

        # Pills/Tags chọn nhanh
        for g in all_groups:
            is_checked = str(g.id) in selected_ids
            sel_class = "group-pill selected" if is_checked else "group-pill"
            check_mark = "✓" if is_checked else "+"
            html.append(f'''
            <div class="{sel_class}" id="{widget_id}_pill_{g.id}" onclick="toggleGroupPill('{widget_id}', '{g.id}')">
                <span class="group-pill-icon" id="{widget_id}_icon_{g.id}">{check_mark}</span>
                <span>{g.name}</span>
            </div>
            ''')

        # Nút chọn nhanh / bỏ chọn
        html.append(f'''
        <div class="group-actions-bar">
            <button type="button" class="btn-group-action" onclick="toggleAllGroupPills('{widget_id}', true)">Chọn tất cả</button>
            <button type="button" class="btn-group-action" onclick="toggleAllGroupPills('{widget_id}', false)">Bỏ chọn</button>
        </div>
        ''')

        html.append('</div>')

        # Javascript điều khiển Group Pills
        html.append(f'''
        <script>
        function toggleGroupPill(widgetId, groupId) {{
            const selectEl = document.getElementById(widgetId);
            const pillEl = document.getElementById(widgetId + '_pill_' + groupId);
            const iconEl = document.getElementById(widgetId + '_icon_' + groupId);
            
            for (let i = 0; i < selectEl.options.length; i++) {{
                if (selectEl.options[i].value === groupId) {{
                    const newStatus = !selectEl.options[i].selected;
                    selectEl.options[i].selected = newStatus;
                    if (newStatus) {{
                        pillEl.classList.add('selected');
                        iconEl.innerText = '✓';
                    }} else {{
                        pillEl.classList.remove('selected');
                        iconEl.innerText = '+';
                    }}
                    break;
                }}
            }}
        }}

        function toggleAllGroupPills(widgetId, selectAll) {{
            const selectEl = document.getElementById(widgetId);
            for (let i = 0; i < selectEl.options.length; i++) {{
                selectEl.options[i].selected = selectAll;
                const gid = selectEl.options[i].value;
                const pillEl = document.getElementById(widgetId + '_pill_' + gid);
                const iconEl = document.getElementById(widgetId + '_icon_' + gid);
                if (pillEl && iconEl) {{
                    if (selectAll) {{
                        pillEl.classList.add('selected');
                        iconEl.innerText = '✓';
                    }} else {{
                        pillEl.classList.remove('selected');
                        iconEl.innerText = '+';
                    }}
                }}
            }}
        }}
        </script>
        ''')

        return mark_safe("".join(html))


# ------------------------------------------------------------------------------
# 2. WIDGET PHÂN QUYỀN THEO MỤC MENU KÈM BỘ LỌC NHANH (QUICK TABS FILTER)
# ------------------------------------------------------------------------------
class MenuGranularPermissionsWidget(forms.SelectMultiple):
    """
    Widget phân quyền trực quan chia theo 7 nhóm menu Sidebar.
    Tích hợp bộ lọc Tab nhanh theo từng mục menu để không phải cuộn lướt.
    Căn lề chuẩn mực đồng nhất với giao diện Unfold.
    Hoàn toàn không sử dụng biểu tượng cảm xúc (emoji/icon trang trí).
    """
    def __init__(self, attrs=None, choices=()):
        super().__init__(attrs, choices)

    def render(self, name, value, attrs=None, renderer=None):
        if value is None:
            value = []
        elif not isinstance(value, (list, tuple)):
            value = [value]
        
        selected_ids = set(str(v) for v in value)

        all_perms = Permission.objects.select_related('content_type').all()
        perm_map = {f"{p.content_type.app_label}.{p.codename}": p for p in all_perms}
        used_perm_ids = set()

        sections_data = []
        for sec in MENU_SECTIONS_DEFINITION:
            sec_items = []
            for codename, label in sec["permissions"]:
                p = perm_map.get(codename)
                if p:
                    used_perm_ids.add(p.id)
                    sec_items.append({
                        "id": p.id,
                        "codename": codename,
                        "label": label,
                        "checked": str(p.id) in selected_ids,
                    })
            sections_data.append({
                "id": sec["id"],
                "short_title": sec["short_title"],
                "title": sec["title"],
                "desc": sec["desc"],
                "items": sec_items,
            })

        other_items = []
        for p in all_perms:
            if p.id not in used_perm_ids:
                other_items.append({
                    "id": p.id,
                    "codename": f"{p.content_type.app_label}.{p.codename}",
                    "label": f"[{p.content_type.app_label}] {p.name}",
                    "checked": str(p.id) in selected_ids,
                })

        widget_id = attrs.get('id', f'id_{name}')
        html = []
        html.append(f'<div class="menu-perm-manager-container" id="{widget_id}_container">')
        
        # CSS Styling - Đồng nhất căn lề và Responsive 100%
        html.append('''
        <style>
            /* Căn lề đồng nhất toàn bộ khối field permissions và user_permissions */
            .field-permissions, .field-user_permissions, .field-groups {
                display: flex !important;
                flex-direction: column !important;
                align-items: stretch !important;
                width: 100% !important;
                padding-left: 12px !important;
                padding-right: 12px !important;
            }
            .field-permissions > div:first-child,
            .field-user_permissions > div:first-child,
            .field-groups > div:first-child {
                min-width: 100% !important;
                width: 100% !important;
                max-width: 100% !important;
                height: auto !important;
                display: block !important;
                margin-bottom: 8px !important;
                padding: 0 !important;
            }
            .field-permissions > div:first-child label,
            .field-user_permissions > div:first-child label,
            .field-groups > div:first-child label {
                width: 100% !important;
                display: block !important;
                margin-bottom: 4px !important;
                font-size: 13px !important;
                font-weight: 700 !important;
                color: #334155 !important;
                text-transform: uppercase;
                letter-spacing: 0.025em;
            }
            .dark .field-permissions > div:first-child label,
            .dark .field-user_permissions > div:first-child label,
            .dark .field-groups > div:first-child label {
                color: #94a3b8 !important;
            }
            .field-permissions > .grow, .field-user_permissions > .grow, .field-groups > .grow {
                width: 100% !important;
                flex-grow: 1 !important;
            }

            .menu-perm-manager-container {
                font-family: inherit;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: #ffffff;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                overflow: hidden;
                width: 100%;
                margin-top: 4px;
            }
            .dark .menu-perm-manager-container {
                background: #1e293b;
                border-color: #334155;
            }
            
            /* Thanh Presets & Tìm kiếm */
            .perm-toolbar {
                padding: 10px 14px;
                background: #f8fafc;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                align-items: center;
                justify-content: space-between;
            }
            .dark .perm-toolbar {
                background: #0f172a;
                border-color: #334155;
            }
            .perm-preset-group {
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                align-items: center;
            }
            .perm-preset-label {
                font-size: 12px;
                font-weight: 600;
                color: #475569;
                margin-right: 2px;
            }
            .dark .perm-preset-label {
                color: #94a3b8;
            }
            .btn-perm-preset {
                padding: 4px 9px;
                font-size: 12px;
                font-weight: 500;
                border-radius: 5px;
                border: 1px solid #cbd5e1;
                background: #ffffff;
                color: #334155;
                cursor: pointer;
                transition: all 0.15s ease;
            }
            .btn-perm-preset:hover {
                background: #f1f5f9;
                border-color: #94a3b8;
                color: #0f172a;
            }
            .dark .btn-perm-preset {
                background: #1e293b;
                border-color: #475569;
                color: #cbd5e1;
            }
            .dark .btn-perm-preset:hover {
                background: #334155;
                color: #ffffff;
            }
            .btn-perm-preset.primary {
                background: #2563eb;
                border-color: #1d4ed8;
                color: #ffffff;
            }
            .btn-perm-preset.primary:hover {
                background: #1d4ed8;
            }
            .btn-perm-preset.danger {
                background: #fef2f2;
                border-color: #fecaca;
                color: #b91c1c;
            }
            .btn-perm-preset.danger:hover {
                background: #fee2e2;
            }
            .perm-search-box {
                padding: 5px 10px;
                font-size: 12px;
                border-radius: 5px;
                border: 1px solid #cbd5e1;
                width: 220px;
                background: #ffffff;
            }
            .dark .perm-search-box {
                background: #1e293b;
                border-color: #475569;
                color: #ffffff;
            }

            /* THANH LỌC NHANH THEO MỤC MENU (QUICK TABS FILTER) */
            .perm-filter-bar {
                padding: 8px 14px;
                background: #ffffff;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                flex-wrap: wrap;
                gap: 6px;
                align-items: center;
            }
            .dark .perm-filter-bar {
                background: #1e293b;
                border-color: #334155;
            }
            .filter-tab-label {
                font-size: 12px;
                font-weight: 600;
                color: #64748b;
                margin-right: 4px;
            }
            .dark .filter-tab-label {
                color: #94a3b8;
            }
            .btn-filter-tab {
                padding: 4px 10px;
                font-size: 12px;
                font-weight: 500;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
                background: #f8fafc;
                color: #475569;
                cursor: pointer;
                transition: all 0.15s ease;
            }
            .btn-filter-tab:hover {
                background: #e2e8f0;
                color: #0f172a;
            }
            .dark .btn-filter-tab {
                background: #0f172a;
                border-color: #334155;
                color: #94a3b8;
            }
            .dark .btn-filter-tab:hover {
                background: #334155;
                color: #f1f5f9;
            }
            .btn-filter-tab.active {
                background: #eff6ff !important;
                border-color: #3b82f6 !important;
                color: #1d4ed8 !important;
                font-weight: 600;
            }
            .dark .btn-filter-tab.active {
                background: #1e3a8a !important;
                border-color: #60a5fa !important;
                color: #dbeafe !important;
            }

            /* Accordion Sections */
            .perm-accordion-item {
                border-bottom: 1px solid #e2e8f0;
            }
            .dark .perm-accordion-item {
                border-color: #334155;
            }
            .perm-accordion-item:last-child {
                border-bottom: none;
            }
            .perm-accordion-header {
                padding: 10px 14px;
                background: #ffffff;
                display: flex;
                align-items: center;
                justify-content: space-between;
                cursor: pointer;
                user-select: none;
                transition: background 0.15s ease;
            }
            .perm-accordion-header:hover {
                background: #f8fafc;
            }
            .dark .perm-accordion-header {
                background: #1e293b;
            }
            .dark .perm-accordion-header:hover {
                background: #334155;
            }
            .perm-title-group {
                display: flex;
                flex-direction: column;
                gap: 2px;
            }
            .perm-section-title {
                font-size: 13px;
                font-weight: 700;
                color: #1e293b;
            }
            .dark .perm-section-title {
                color: #f1f5f9;
            }
            .perm-section-desc {
                font-size: 12px;
                color: #64748b;
            }
            .dark .perm-section-desc {
                color: #94a3b8;
            }
            .perm-header-actions {
                display: flex;
                align-items: center;
                gap: 8px;
            }
            .perm-count-badge {
                padding: 2px 7px;
                font-size: 11px;
                font-weight: 600;
                border-radius: 12px;
                background: #e2e8f0;
                color: #475569;
            }
            .perm-count-badge.active {
                background: #dbeafe;
                color: #1d4ed8;
            }
            .dark .perm-count-badge {
                background: #334155;
                color: #cbd5e1;
            }
            .dark .perm-count-badge.active {
                background: #1e3a8a;
                color: #93c5fd;
            }
            .btn-mini-action {
                padding: 2px 7px;
                font-size: 11px;
                background: none;
                border: 1px solid #cbd5e1;
                border-radius: 4px;
                color: #475569;
                cursor: pointer;
            }
            .btn-mini-action:hover {
                background: #f1f5f9;
                color: #0f172a;
            }
            .dark .btn-mini-action {
                border-color: #475569;
                color: #cbd5e1;
            }
            .perm-accordion-body {
                padding: 10px 14px 14px 14px;
                background: #f8fafc;
                border-top: 1px solid #e2e8f0;
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
                gap: 6px 14px;
            }
            .dark .perm-accordion-body {
                background: #0f172a;
                border-color: #334155;
            }
            .perm-checkbox-item {
                display: flex;
                align-items: flex-start;
                gap: 8px;
                font-size: 13px;
                color: #334155;
                padding: 4px 6px;
                border-radius: 4px;
                cursor: pointer;
            }
            .perm-checkbox-item:hover {
                background: #e2e8f0;
            }
            .dark .perm-checkbox-item {
                color: #cbd5e1;
            }
            .dark .perm-checkbox-item:hover {
                background: #1e293b;
            }
            .perm-checkbox-item input[type="checkbox"] {
                margin-top: 3px;
                accent-color: #2563eb;
                cursor: pointer;
            }
        </style>
        ''')

        # 1. Thanh Presets & Tìm kiếm
        html.append('<div class="perm-toolbar">')
        html.append('  <div class="perm-preset-group">')
        html.append('    <span class="perm-preset-label">Mẫu phân quyền:</span>')
        html.append(f'    <button type="button" class="btn-perm-preset" onclick="applyPermPreset(\'{widget_id}\', \'doctor\')">Bác sĩ điều trị</button>')
        html.append(f'    <button type="button" class="btn-perm-preset" onclick="applyPermPreset(\'{widget_id}\', \'reception\')">Lễ tân tiếp đón</button>')
        html.append(f'    <button type="button" class="btn-perm-preset" onclick="applyPermPreset(\'{widget_id}\', \'cashier\')">Thu ngân thanh toán</button>')
        html.append(f'    <button type="button" class="btn-perm-preset" onclick="applyPermPreset(\'{widget_id}\', \'marketing\')">Marketing truyền thông</button>')
        html.append(f'    <button type="button" class="btn-perm-preset primary" onclick="applyPermPreset(\'{widget_id}\', \'all\')">Toàn quyền</button>')
        html.append(f'    <button type="button" class="btn-perm-preset danger" onclick="applyPermPreset(\'{widget_id}\', \'none\')">Bỏ chọn tất cả</button>')
        html.append('  </div>')
        html.append('  <div>')
        html.append(f'    <input type="text" class="perm-search-box" placeholder="Tìm kiếm quyền hạn..." oninput="filterPermissions(\'{widget_id}\', this.value)" />')
        html.append('  </div>')
        html.append('</div>')

        # 2. THANH LỌC NHANH THEO MỤC MENU (QUICK TABS FILTER)
        html.append('<div class="perm-filter-bar">')
        html.append('  <span class="filter-tab-label">Lọc nhanh mục menu:</span>')
        html.append(f'  <button type="button" class="btn-filter-tab active" id="{widget_id}_tab_all" onclick="filterMenuSection(\'{widget_id}\', \'all\')">Tất cả các mục (7)</button>')
        for sec in sections_data:
            html.append(f'  <button type="button" class="btn-filter-tab" id="{widget_id}_tab_{sec["id"]}" onclick="filterMenuSection(\'{widget_id}\', \'{sec["id"]}\')">{sec["short_title"]}</button>')
        html.append('</div>')

        # Hidden Multi-Select thực tế
        html.append(f'<select name="{name}" id="{widget_id}" multiple style="display: none;">')
        for p in all_perms:
            is_sel = 'selected' if str(p.id) in selected_ids else ''
            html.append(f'<option value="{p.id}" data-codename="{p.content_type.app_label}.{p.codename}" {is_sel}>{p.name}</option>')
        html.append('</select>')

        # 3. 7 Khối Accordion theo Menu
        html.append('<div class="perm-accordion-wrapper">')
        for sec in sections_data:
            sec_id = sec["id"]
            checked_count = sum(1 for item in sec["items"] if item["checked"])
            total_count = len(sec["items"])
            badge_class = "perm-count-badge active" if checked_count > 0 else "perm-count-badge"

            html.append(f'<div class="perm-accordion-item" id="{widget_id}_{sec_id}" data-sec-root="{sec_id}">')
            html.append(f'  <div class="perm-accordion-header" onclick="togglePermSection(\'{widget_id}_{sec_id}_body\')">')
            html.append('    <div class="perm-title-group">')
            html.append(f'      <div class="perm-section-title">{sec["title"]}</div>')
            html.append(f'      <div class="perm-section-desc">{sec["desc"]}</div>')
            html.append('    </div>')
            html.append('    <div class="perm-header-actions" onclick="event.stopPropagation();">')
            html.append(f'      <span class="{badge_class}" id="{widget_id}_{sec_id}_count">{checked_count}/{total_count} quyền</span>')
            html.append(f'      <button type="button" class="btn-mini-action" onclick="toggleSectionChecks(\'{widget_id}\', \'{sec_id}\', true)">Chọn mục này</button>')
            html.append(f'      <button type="button" class="btn-mini-action" onclick="toggleSectionChecks(\'{widget_id}\', \'{sec_id}\', false)">Bỏ chọn</button>')
            html.append('    </div>')
            html.append('  </div>')

            html.append(f'  <div class="perm-accordion-body" id="{widget_id}_{sec_id}_body">')
            for item in sec["items"]:
                is_chk = 'checked' if item["checked"] else ''
                html.append(f'    <label class="perm-checkbox-item" data-codename="{item["codename"]}">')
                html.append(f'      <input type="checkbox" data-sec="{sec_id}" value="{item["id"]}" {is_chk} onchange="syncPermToSelect(\'{widget_id}\', this)" />')
                html.append(f'      <span><strong>{item["label"]}</strong> <small style="color: #64748b; display: block; font-size: 11px;">({item["codename"]})</small></span>')
                html.append('    </label>')
            html.append('  </div>')
            html.append('</div>')

        # Khối phụ: Các quyền hệ thống khác (nếu có)
        if other_items:
            sec_id = "sec_other"
            checked_count = sum(1 for item in other_items if item["checked"])
            total_count = len(other_items)
            badge_class = "perm-count-badge active" if checked_count > 0 else "perm-count-badge"
            html.append(f'<div class="perm-accordion-item" id="{widget_id}_{sec_id}" data-sec-root="{sec_id}">')
            html.append(f'  <div class="perm-accordion-header" onclick="togglePermSection(\'{widget_id}_{sec_id}_body\')">')
            html.append('    <div class="perm-title-group">')
            html.append('      <div class="perm-section-title">8. Quyền hạn Hệ thống Khác (Nâng cao)</div>')
            html.append('      <div class="perm-section-desc">Các quyền kỹ thuật hệ thống Django mặc định</div>')
            html.append('    </div>')
            html.append('    <div class="perm-header-actions" onclick="event.stopPropagation();">')
            html.append(f'      <span class="{badge_class}" id="{widget_id}_{sec_id}_count">{checked_count}/{total_count} quyền</span>')
            html.append(f'      <button type="button" class="btn-mini-action" onclick="toggleSectionChecks(\'{widget_id}\', \'{sec_id}\', true)">Chọn mục này</button>')
            html.append(f'      <button type="button" class="btn-mini-action" onclick="toggleSectionChecks(\'{widget_id}\', \'{sec_id}\', false)">Bỏ chọn</button>')
            html.append('    </div>')
            html.append('  </div>')
            html.append(f'  <div class="perm-accordion-body" id="{widget_id}_{sec_id}_body" style="display: none;">')
            for item in other_items:
                is_chk = 'checked' if item["checked"] else ''
                html.append(f'    <label class="perm-checkbox-item" data-codename="{item["codename"]}">')
                html.append(f'      <input type="checkbox" data-sec="{sec_id}" value="{item["id"]}" {is_chk} onchange="syncPermToSelect(\'{widget_id}\', this)" />')
                html.append(f'      <span><strong>{item["label"]}</strong> <small style="color: #64748b; display: block; font-size: 11px;">({item["codename"]})</small></span>')
                html.append('    </label>')
            html.append('  </div>')
            html.append('</div>')

        html.append('</div>') # end perm-accordion-wrapper
        html.append('</div>') # end container

        # Javascript Điều khiển Tương tác
        html.append(f'''
        <script>
        function filterMenuSection(widgetId, targetSecId) {{
            const container = document.getElementById(widgetId + '_container');
            const items = container.querySelectorAll('.perm-accordion-item');
            const tabs = container.querySelectorAll('.btn-filter-tab');

            // Cập nhật tab active
            tabs.forEach(t => t.classList.remove('active'));
            const activeTab = document.getElementById(widgetId + '_tab_' + targetSecId);
            if (activeTab) activeTab.classList.add('active');

            items.forEach(item => {{
                const secId = item.getAttribute('data-sec-root');
                const body = document.getElementById(widgetId + '_' + secId + '_body');
                if (targetSecId === 'all') {{
                    item.style.display = 'block';
                    if (body && secId !== 'sec_other') body.style.display = 'grid';
                }} else if (secId === targetSecId) {{
                    item.style.display = 'block';
                    if (body) body.style.display = 'grid';
                    item.scrollIntoView({{ behavior: 'smooth', block: 'nearest' }});
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}

        function togglePermSection(bodyId) {{
            const el = document.getElementById(bodyId);
            if (el) {{
                el.style.display = (el.style.display === 'none') ? 'grid' : 'none';
            }}
        }}

        function syncPermToSelect(widgetId, checkbox) {{
            const selectEl = document.getElementById(widgetId);
            const val = checkbox.value;
            for (let i = 0; i < selectEl.options.length; i++) {{
                if (selectEl.options[i].value === val) {{
                    selectEl.options[i].selected = checkbox.checked;
                    break;
                }}
            }}
            updatePermCounts(widgetId);
        }}

        function toggleSectionChecks(widgetId, secId, checkAll) {{
            const container = document.getElementById(widgetId + '_container');
            const checkboxes = container.querySelectorAll('input[data-sec="' + secId + '"]');
            checkboxes.forEach(cb => {{
                cb.checked = checkAll;
                syncPermToSelect(widgetId, cb);
            }});
        }}

        function updatePermCounts(widgetId) {{
            const container = document.getElementById(widgetId + '_container');
            const sections = container.querySelectorAll('.perm-accordion-item');
            sections.forEach(sec => {{
                const secId = sec.getAttribute('data-sec-root');
                const checkboxes = sec.querySelectorAll('input[type="checkbox"]');
                const checked = sec.querySelectorAll('input[type="checkbox"]:checked');
                const badge = document.getElementById(widgetId + '_' + secId + '_count');
                if (badge) {{
                    badge.innerText = checked.length + '/' + checkboxes.length + ' quyền';
                    if (checked.length > 0) {{
                        badge.className = 'perm-count-badge active';
                    }} else {{
                        badge.className = 'perm-count-badge';
                    }}
                }}
            }});
        }}

        function applyPermPreset(widgetId, presetName) {{
            const container = document.getElementById(widgetId + '_container');
            const allCbs = container.querySelectorAll('input[type="checkbox"]');
            
            // Xóa hết trước
            allCbs.forEach(cb => cb.checked = false);

            if (presetName === 'all') {{
                allCbs.forEach(cb => cb.checked = true);
            }} else if (presetName === 'doctor') {{
                const targetCodenamePatterns = [
                    'booking.view_booking', 'booking.change_booking',
                    'operations.view_dailyschedule', 'operations.view_weeklyschedule', 'operations.view_managebooking',
                    'booking.view_customer', 'booking.change_customer',
                    'booking.view_servicedetail', 'booking.view_commissionrate',
                    'booking.view_inventorydetail', 'booking.add_inventoryusage'
                ];
                allCbs.forEach(cb => {{
                    const label = cb.closest('label');
                    const code = label ? label.getAttribute('data-codename') : '';
                    if (targetCodenamePatterns.includes(code)) {{
                        cb.checked = true;
                    }}
                }});
            }} else if (presetName === 'reception') {{
                const targetCodenamePatterns = [
                    'booking.view_booking', 'booking.add_booking', 'booking.change_booking',
                    'operations.view_dailyschedule', 'operations.view_weeklyschedule', 'operations.view_managebooking',
                    'booking.view_customer', 'booking.add_customer', 'booking.change_customer',
                    'booking.view_clinic', 'booking.view_servicedetail', 'booking.view_timeslot'
                ];
                allCbs.forEach(cb => {{
                    const label = cb.closest('label');
                    const code = label ? label.getAttribute('data-codename') : '';
                    if (targetCodenamePatterns.includes(code)) {{
                        cb.checked = true;
                    }}
                }});
            }} else if (presetName === 'cashier') {{
                const targetCodenamePatterns = [
                    'booking.view_payment', 'booking.add_payment', 'booking.change_payment',
                    'booking.view_bookingbill', 'booking.add_bookingbill',
                    'booking.view_customer', 'booking.view_booking'
                ];
                allCbs.forEach(cb => {{
                    const label = cb.closest('label');
                    const code = label ? label.getAttribute('data-codename') : '';
                    if (targetCodenamePatterns.includes(code)) {{
                        cb.checked = true;
                    }}
                }});
            }} else if (presetName === 'marketing') {{
                const targetCodenamePatterns = [
                    'booking.manage_wordpress_posts', 'booking.view_article', 'booking.add_article', 'booking.change_article',
                    'booking.view_menulink', 'booking.change_menulink', 'booking.view_sitesettings', 'booking.change_sitesettings',
                    'booking.view_servicecategory', 'booking.view_servicedetail'
                ];
                allCbs.forEach(cb => {{
                    const label = cb.closest('label');
                    const code = label ? label.getAttribute('data-codename') : '';
                    if (targetCodenamePatterns.includes(code)) {{
                        cb.checked = true;
                    }}
                }});
            }}

            // Sync toàn bộ lên select
            allCbs.forEach(cb => syncPermToSelect(widgetId, cb));
            updatePermCounts(widgetId);
        }}

        function filterPermissions(widgetId, query) {{
            const q = query.trim().toLowerCase();
            const container = document.getElementById(widgetId + '_container');
            const items = container.querySelectorAll('.perm-checkbox-item');
            items.forEach(item => {{
                const text = item.innerText.toLowerCase();
                const code = (item.getAttribute('data-codename') || '').toLowerCase();
                if (q === '' || text.includes(q) || code.includes(q)) {{
                    item.style.display = 'flex';
                }} else {{
                    item.style.display = 'none';
                }}
            }});
        }}
        </script>
        ''')

        return mark_safe("".join(html))
