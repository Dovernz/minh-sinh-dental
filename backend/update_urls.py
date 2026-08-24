file_path = "core/urls.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

if "auth_views" not in content:
    content = content.replace("from django.urls import path, include", "from django.urls import path, include\nfrom django.contrib.auth import views as auth_views")
    
    new_urls = """path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/', admin.site.urls),"""
    
    content = content.replace("path('admin/', admin.site.urls),", new_urls)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
