import os
import re

file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Split out the UNFOLD config and reconstruct it to ensure correctness
if "UNFOLD =" in content:
    content = content.split("UNFOLD =")[0]

unfold_config = """UNFOLD = {
    "SITE_TITLE": "Nha Khoa Minh Sinh",
    "SITE_HEADER": "Nha Khoa Minh Sinh",
    "SITE_LOGO": "/static/img/logo.jpg",
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
                        "link": "/admin/booking/inventorydetail/",
                    },
                    {
                        "title": "Tiêu hao Vật tư",
                        "icon": "history",
                        "link": "/admin/booking/inventoryusage/",
                    },
                ],
            },
            {
                "title": "Hệ thống & Quản trị User",
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
                        "title": "Nhân viên",
                        "icon": "badge",
                        "link": "/admin/booking/employee/",
                    },
                ],
            },
            {
                "title": "Marketing",
                "icon": "campaign",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Bài viết",
                        "icon": "article",
                        "link": "/admin/booking/article/",
                    },
                ],
            },
            {
                "title": "Database",
                "icon": "database",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Articles",
                        "icon": "article",
                        "link": "/admin/booking/article/",
                    },
                    {
                        "title": "Billing (Hóa đơn)",
                        "icon": "receipt_long",
                        "link": "/admin/booking/billing/",
                    },
                    {
                        "title": "Booking details",
                        "icon": "list",
                        "link": "/admin/booking/bookingdetail/",
                    },
                    {
                        "title": "Booking status historys",
                        "icon": "history",
                        "link": "/admin/booking/bookingstatushistory/",
                    },
                    {
                        "title": "Bookings",
                        "icon": "table_view",
                        "link": "/admin/booking/booking/",
                    },
                    {
                        "title": "Cấu hình Thanh toán",
                        "icon": "settings",
                        "link": "/admin/booking/topupinfo/",
                    },
                    {
                        "title": "Chi tiết Dịch vụ",
                        "icon": "medical_services",
                        "link": "/admin/booking/servicedetail/",
                    },
                    {
                        "title": "Clinics",
                        "icon": "store",
                        "link": "/admin/booking/clinic/",
                    },
                    {
                        "title": "Customers",
                        "icon": "people",
                        "link": "/admin/booking/customer/",
                    },
                    {
                        "title": "Danh mục Dịch vụ",
                        "icon": "category",
                        "link": "/admin/booking/servicecategory/",
                    },
                    {
                        "title": "Discounts",
                        "icon": "local_offer",
                        "link": "/admin/services_menu/catalogdiscount/",
                    },
                    {
                        "title": "Employees",
                        "icon": "badge",
                        "link": "/admin/booking/employee/",
                    },
                    {
                        "title": "Inventory details",
                        "icon": "inventory_2",
                        "link": "/admin/booking/inventorydetail/",
                    },
                    {
                        "title": "Inventory usages",
                        "icon": "history",
                        "link": "/admin/booking/inventoryusage/",
                    },
                    {
                        "title": "Payments",
                        "icon": "payments",
                        "link": "/admin/booking/payment/",
                    },
                    {
                        "title": "Time slots",
                        "icon": "schedule",
                        "link": "/admin/booking/timeslot/",
                    },
                ],
            },
        ],
    },
}
"""

# Wait, what if there were other configs after UNFOLD? 
# In previous steps, we always used `content.split("UNFOLD =")[0]` and appended the `UNFOLD` config to the end.
# So I'll just append it to the end again, making sure we don't lose the EMAIL_BACKEND or LOGIN_REDIRECT_URL!
# BUT WAIT. In my previous scripts, `content = content.split("UNFOLD =")[0]` actually TRUNCATED the file.
# Did I lose EMAIL_BACKEND and LOGIN_REDIRECT_URL when I did that previously?
# Let's check `core/settings.py` for EMAIL_BACKEND and LOGIN_REDIRECT_URL.
