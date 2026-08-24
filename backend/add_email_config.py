file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

if "EMAIL_BACKEND" not in content:
    email_config = """
# Email SMTP Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'email_cua_phong_kham@gmail.com'  # Thay bằng email thật
EMAIL_HOST_PASSWORD = 'app_password_tao_tu_gmail' # Mật khẩu ứng dụng
DEFAULT_FROM_EMAIL = 'Nha Khoa Minh Sinh <email_cua_phong_kham@gmail.com>'
"""
    content += email_config
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
