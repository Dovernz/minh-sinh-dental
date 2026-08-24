import os
import re

file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

if "UNFOLD =" in content:
    content = content.split("UNFOLD =")[0]

unfold_config = """UNFOLD = {
    "SITE_TITLE": "Nha Khoa Minh Sinh",
    "SITE_HEADER": "Nha Khoa Minh Sinh",
    "SITE_ICON": lambda request: static("img/logo.png"),
    "SITE_LOGO": lambda request: static("img/logo.png"),
    "STYLES": [
        lambda request: static("css/admin_custom.css"),
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "Quản lý Booking",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Lịch Ngày",
                        "icon": "calendar_today",
                        "link": "/admin/operations/dailyschedule/",
                    },
                    {
                        "title": "Lịch Tuần",
                        "icon": "calendar_view_week",
                        "link": "/admin/operations/weeklyschedule/",
                    },
                    {
                        "title": "Chi tiết Bookings",
                        "icon": "list_alt",
                        "link": "/admin/operations/managebooking/",
                    },
                ],
            },
            {
                "title": "Khách hàng & Dịch vụ",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Khách hàng",
                        "icon": "people",
                        "link": "/admin/booking/customer/",
                    },
                    {
                        "title": "Cơ sở (Clinics)",
                        "icon": "store",
                        "link": "/admin/booking/clinic/",
                    },
                    {
                        "title": "Nhân viên",
                        "icon": "badge",
                        "link": "/admin/booking/employee/",
                    },
                    {
                        "title": "Danh mục Dịch vụ",
                        "icon": "category",
                        "link": "/admin/booking/servicecategory/",
                    },
                    {
                        "title": "Chi tiết Dịch vụ",
                        "icon": "medical_services",
                        "link": "/admin/booking/servicedetail/",
                    },
                    {
                        "title": "Khung giờ",
                        "icon": "schedule",
                        "link": "/admin/booking/timeslot/",
                    },
                ],
            },
            {
                "title": "Tài chính & Vật tư",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Hóa đơn",
                        "icon": "receipt_long",
                        "link": "/admin/booking/billing/",
                    },
                    {
                        "title": "Thanh toán",
                        "icon": "payments",
                        "link": "/admin/booking/payment/",
                    },
                    {
                        "title": "Vật tư Kho",
                        "icon": "inventory_2",
                        "link": "/admin/booking/inventoryitem/",
                    },
                    {
                        "title": "Tiêu hao Vật tư",
                        "icon": "history",
                        "link": "/admin/booking/inventoryusage/",
                    },
                ],
            },
            {
                "title": "Hệ thống & Marketing",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Quản trị viên (Users)",
                        "icon": "manage_accounts",
                        "link": "/admin/auth/user/",
                    },
                    {
                        "title": "Nhóm quyền (Groups)",
                        "icon": "group",
                        "link": "/admin/auth/group/",
                    },
                    {
                        "title": "Bài viết",
                        "icon": "article",
                        "link": "/admin/booking/article/",
                    },
                ],
            },
        ],
    },
}
"""
content += unfold_config
with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("done")
