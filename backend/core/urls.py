from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/', admin.site.urls),
    path('api/', include('booking.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

admin.site.site_header = "Nha Khoa Minh Sinh"
admin.site.site_title = "Nha Khoa Minh Sinh"
admin.site.index_title = "Bảng điều khiển"
