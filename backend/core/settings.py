import os
from pathlib import Path
import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Khá»Ÿi tạo django-environ
env = environ.Env(
    DEBUG=(bool, False)
)

# Đọc các biến môi trường từ file .env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG')

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'unfold',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'cloudinary',
    
    # Third party
    'rest_framework',
    'corsheaders',
    'storages',
    'import_export',
    'ckeditor',
    'ckeditor_uploader',
    
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
        'toolbar': 'full',
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

UNFOLD = {
    "SITE_TITLE": "Nha Khoa Minh Sinh",
    "SITE_HEADER": "Nha Khoa Minh Sinh",
    # "SITE_LOGO": "/static/img/logo.jpg",

    "STYLES": [
        lambda request: static("css/admin_custom.css"),
    ],
    "SCRIPTS": [
        '/static/js/live_search.js',
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
                    {
                        "title": "Tạo Booking",
                        "icon": "add_circle",
                        "link": "/admin/booking-embed/",
                    },
                ],
            },
            {
                "title": "Giao dịch",
                "separator": True,
                "collapsible": True,
                "items": [
                    {
                        "title": "Thanh toán (POS)",
                        "icon": "point_of_sale",
                        "link": "/admin/pos-system/",
                                            },
                    {
                        "title": "Danh sách Hóa đơn",
                        "icon": "receipt_long",
                        "link": "/admin/booking/billing/",
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
                    {
                        "title": "Khuyến mãi",
                        "icon": "local_offer",
                        "link": reverse_lazy("admin:services_menu_catalogdiscount_changelist"),
                    },
                ],
            },
            {
                "title": "Tài chính & Vật tư",
                "separator": True,
                "collapsible": True,
                "items": [
                    
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

# Email SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'ctt130303@gmail.com'  # Thay bằng email thật
EMAIL_HOST_PASSWORD = 'ebju xwfb qvja ffrh' # Mật khẩu ứng dụng
DEFAULT_FROM_EMAIL = 'Nha Khoa Minh Sinh <ctt130303@gmail.com>'

# Điều hÆ°á»›ng sau khi ÄÄƒng nhập/ÄÄƒng xuất
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/login/'

import os
import cloudinary
import cloudinary.uploader
import cloudinary.api

# C?u hình luu tr? file upload (Media) lên Cloudinary
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'


