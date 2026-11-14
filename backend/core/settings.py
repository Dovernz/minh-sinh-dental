import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# KhÃ¡Â»Å¸i táº¡o django-environ
env = environ.Env(
    DEBUG=(bool, False)
)

# Ã„ÂÃ¡Â»Âc cÃ¡c biáº¿n mÃ´i trÆ°Ã¡Â»Âng tá»« file .env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    '*',
    '103.78.1.84',
    'minhsinhdental.com',
    '.minhsinhdental.com',
    'localhost',
    '127.0.0.1',
])

# Application definition

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.humanize',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    
    # Third party
    'rest_framework',
    'corsheaders',
    'storages',
    'import_export',
    'tinymce',
    
    # Local apps
    'booking',
    'operations',
    'services_menu',
    'marketing',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

import dj_database_url

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(default=env('DATABASE_URL'))
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'vi'

TIME_ZONE = 'Asia/Ho_Chi_Minh'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'http://localhost',
    'http://127.0.0.1',
    'http://localhost:80',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://103.78.1.84',
    'http://uat.minhsinhdental.com',
    'https://uat.minhsinhdental.com',
    'http://minhsinhdental.com',
    'https://minhsinhdental.com',
    'http://*.minhsinhdental.com',
    'https://*.minhsinhdental.com',
])

# Supabase S3 Configuration
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='your-access-key')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='your-secret-key')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='your-bucket-name')
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL', default='https://your-project-ref.supabase.co/storage/v1/s3')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='ap-southeast-1')
AWS_S3_FILE_OVERWRITE = False

SUPABASE_FOLDER = env('SUPABASE_FOLDER', default='media')
AWS_LOCATION = SUPABASE_FOLDER

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# CKEditor Configuration
CKEDITOR_UPLOAD_PATH = 'uploads/'
CKEDITOR_CONFIGS = {
    'default': {
        'skin': 'moono-lisa',
        'toolbar': '|f|u|l|l|',
        'height': 500,
        'width': '100%',
        'tabSpaces': 4,
        'extraPlugins': ','.join(['uploadimage', 'codesnippet', 'font', 'colorbutton', 'justify']),
    },
}

from django.urls import reverse_lazy


STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

from django.urls import reverse_lazy
from django.templatetags.static import static

SSO_SECRET_KEY = env('SSO_SECRET_KEY', default='minhsinh_dental_sso_secure_key_2026')

def check_section_perm(request, perms):
    if not request.user or not request.user.is_authenticated:
        return False
    if request.user.is_superuser:
        return True
    return any(request.user.has_perm(p) for p in perms)

def has_booking_perm(request):
    return check_section_perm(request, [
        'booking.view_booking', 'booking.add_booking', 'booking.change_booking',
        'operations.view_managebooking', 'operations.view_dailyschedule', 'operations.view_weeklyschedule'
    ])

def has_transaction_perm(request):
    return check_section_perm(request, [
        'booking.view_payment', 'booking.add_payment', 'booking.change_payment',
        'booking.view_bookingbill', 'booking.add_bookingbill'
    ])

def has_customer_service_perm(request):
    return check_section_perm(request, [
        'booking.view_customer', 'booking.add_customer', 'booking.change_customer',
        'booking.view_clinic', 'booking.view_service', 'booking.view_servicedetail',
        'booking.view_servicecategory', 'booking.view_timeslot', 'booking.view_catalogdiscount'
    ])

def has_finance_inventory_perm(request):
    return check_section_perm(request, [
        'booking.view_inventorydetail', 'booking.add_inventorydetail', 'booking.change_inventorydetail',
        'booking.view_inventoryusage', 'booking.add_inventoryusage',
        'booking.view_topupinfo', 'booking.view_commissionrate', 'booking.view_payment'
    ])

def has_wordpress_perm(request):
    return check_section_perm(request, [
        'booking.manage_wordpress_posts',
        'booking.view_article', 'booking.add_article', 'booking.change_article',
        'booking.view_marketingarticle'
    ])

def has_web_config_perm(request):
    return check_section_perm(request, [
        'booking.view_menulink', 'booking.add_menulink', 'booking.change_menulink',
        'booking.view_sitesettings', 'booking.change_sitesettings'
    ])

def has_system_user_perm(request):
    return check_section_perm(request, [
        'auth.view_user', 'auth.add_user', 'auth.change_user',
        'auth.view_group', 'auth.add_group', 'auth.change_group',
        'booking.view_employee', 'booking.add_employee', 'booking.change_employee'
    ])

UNFOLD = {
    "INDEX_TITLE": "Báº£ng Ä‘iÃ¡Â»Âu khiÃ¡Â»Æ’n",
    "SITE_TITLE": "Nha Khoa Minh Sinh",
    "SITE_HEADER": "Nha Khoa Minh Sinh",
    # "SITE_LOGO": "/static/img/logo.jpg",

    "STYLES": [
        lambda request: static("css/admin_mobile.css"),
        lambda request: static("css/admin_custom.css") + "?v=66666666",
    ],
    "SCRIPTS": [
        lambda request: static("js/admin_custom.js") + "?v=88888888",
        '/static/js/live_search.js',
    ],
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
                "navigation": [
            {
                "title": "Quản lý Booking",
                "collapsible": True,
                "permission": has_booking_perm,
                "items": [
                    {"title": "Lịch Ngày", "icon": "calendar_today", "link": "/admin/operations/dailyschedule/", "permission": has_booking_perm},
                    {"title": "Lịch Tuần", "icon": "calendar_view_week", "link": "/admin/operations/weeklyschedule/", "permission": has_booking_perm},
                    {"title": "Chi tiết Bookings", "icon": "list_alt", "link": "/admin/operations/managebooking/", "permission": has_booking_perm},
                    {"title": "Tạo Booking", "icon": "add_circle", "link": "/admin/booking-embed/", "permission": has_booking_perm},
                ],
            },
            {
                "title": "Giao dịch",
                "separator": True,
                "collapsible": True,
                "permission": has_transaction_perm,
                "items": [
                    {"title": "Thanh toán (POS)", "icon": "point_of_sale", "link": "/admin/pos-system/", "permission": has_transaction_perm},
                    {"title": "Thu hồi Công nợ", "icon": "price_check", "link": "/admin/pos-debt/", "permission": has_transaction_perm},
                    {"title": "Hóa đơn & Thanh toán", "icon": "receipt_long", "link": "/admin/booking/payment/"},
                ],
            },
            {
                "title": "Khách hàng & Dịch vụ",
                "separator": True,
                "collapsible": True,
                "permission": has_customer_service_perm,
                "items": [
                    {"title": "Khách hàng", "icon": "people", "link": "/admin/booking/customer/"},
                    {"title": "Cơ sở (Clinics)", "icon": "store", "link": "/admin/booking/clinic/"},
                    {"title": "Danh mục Dịch vụ", "icon": "category", "link": "/admin/booking/servicecategory/"},
                    {"title": "Chi tiết Dịch vụ", "icon": "medical_services", "link": "/admin/booking/servicedetail/"},
                    {"title": "Khung giờ", "icon": "schedule", "link": "/admin/booking/timeslot/"},
                    {"title": "Khuyến mãi", "icon": "local_offer", "link": reverse_lazy("admin:services_menu_catalogdiscount_changelist")},
                ],
            },
            {
                "title": "Tài chính & Vật tư",
                "separator": True,
                "collapsible": True,
                "permission": has_finance_inventory_perm,
                "items": [
                    {"title": "Hoa hồng Bác sĩ", "icon": "account_balance", "link": "/admin/commissions-embed/", "permission": has_finance_inventory_perm},
                    {"title": "Cấu hình Thanh toán", "icon": "account_balance_wallet", "link": reverse_lazy("admin:booking_topupinfo_changelist")},
                    {"title": "Vật tư Kho", "icon": "inventory_2", "link": "/admin/booking/inventorydetail/"},
                    {"title": "Tiêu hao Vật tư", "icon": "history", "link": "/admin/booking/inventoryusage/"},
                ],
            },
            {
                "title": "Bài viết & Blog (WordPress)",
                "icon": "campaign",
                "separator": True,
                "collapsible": True,
                "permission": has_wordpress_perm,
                "items": [
                    {
                        "title": "Quản lý Bài viết",
                        "icon": "article",
                        "link": "/admin/sso-to-wordpress/?target=edit.php",
                        "link_attrs": {"target": "_blank", "rel": "noopener noreferrer"},
                        "permission": has_wordpress_perm,
                    },
                    {
                        "title": "Viết Bài Mới",
                        "icon": "post_add",
                        "link": "/admin/sso-to-wordpress/?target=post-new.php",
                        "link_attrs": {"target": "_blank", "rel": "noopener noreferrer"},
                        "permission": has_wordpress_perm,
                    },
                    {
                        "title": "Thư viện Hình ảnh",
                        "icon": "photo_library",
                        "link": "/admin/sso-to-wordpress/?target=upload.php",
                        "link_attrs": {"target": "_blank", "rel": "noopener noreferrer"},
                        "permission": has_wordpress_perm,
                    },
                ],
            },
            {
                "title": "Hệ thống & Quản trị User",
                "separator": True,
                "collapsible": True,
                "permission": has_system_user_perm,
                "items": [
                    {"title": "Cấu hình Commission Rate", "icon": "settings", "link": reverse_lazy("admin:booking_commissionrate_changelist")},
                    {"title": "Phân quyền", "icon": "security", "link": reverse_lazy("admin:auth_group_changelist")},
                    {"title": "Người dùng", "icon": "person", "link": reverse_lazy("admin:auth_user_changelist")},
                    {"title": "Nhân viên", "icon": "badge", "link": "/admin/booking/employee/", "permission": has_system_user_perm},
                ],
            },
        ],
    },
}

# Email SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')  # Thay báº±ng email tháº­t
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='') # Máº­t kháº©u á»©ng dá»¥ng
DEFAULT_FROM_EMAIL = f'Nha Khoa Minh Sinh <{EMAIL_HOST_USER}>'

# Ã„ÂiÃ¡Â»Âu hÆ°Ã¡Â»â€ºng sau khi Ãƒâ€žÃ‚ÂÃƒâ€žÃ†â€™ng nháº­p/Ãƒâ€žÃ‚ÂÃƒâ€žÃ†â€™ng xuáº¥t
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/login/'

import os
import cloudinary
import cloudinary.uploader

import cloudinary
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    cloud_name = env('CLOUDINARY_CLOUD_NAME', default=''),
    api_key = env('CLOUDINARY_API_KEY', default=''),
    api_secret = env('CLOUDINARY_API_SECRET', default=''),
    secure = True
)


# C?u hÃ¬nh luu tr? file upload (Media) lÃªn Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'



STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'


TINYMCE_DEFAULT_CONFIG = {
    'height': 600,
    'menubar': 'file edit view insert format tools table help',
    'plugins': 'advlist autolink lists link image charmap preview anchor searchreplace visualblocks code fullscreen insertdatetime media table code help wordcount',
    'toolbar': 'undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | forecolor backcolor | alignleft aligncenter alignright alignjustify | bullist numlist outdent indent | link image media table | removeformat | fullscreen preview',
    'paste_data_images': True,
    'images_upload_url': '/tinymce/upload/', 
    'file_picker_callback': f'''function (cb, value, meta) {{
        window.cloudinary.createMediaLibrary({{
            cloud_name: '{env("CLOUDINARY_CLOUD_NAME", default="")}',
            api_key: '{env("CLOUDINARY_API_KEY", default="")}',
            multiple: false
        }}, {{
            insertHandler: function (data) {{
                data.assets.forEach(asset => {{
                    cb(asset.secure_url, {{ title: asset.public_id }});
                }});
            }}
        }}).show();
    }}''',
}
# Default password for auto-created employee accounts
DEFAULT_EMPLOYEE_PASSWORD = env('DEFAULT_EMPLOYEE_PASSWORD', default='')

USE_THOUSAND_SEPARATOR = True

USE_L10N = False
DECIMAL_SEPARATOR = '.'
THOUSAND_SEPARATOR = ','
NUMBER_GROUPING = 3


# Allow iframe embedding for Admin and Frontend
X_FRAME_OPTIONS = 'SAMEORIGIN'
