from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.urls import path, include
from booking.views import tinymce_upload
from django.contrib.auth import views as auth_views

@staff_member_required
@staff_member_required
def admin_booking_embed_view(request):
    context = admin.site.each_context(request)
    context['title'] = 'Đặt lịch (Tổng đài)'
    return render(request, 'admin/admin_booking.html', context)

@staff_member_required
def pos_embed_view(request):
    context = admin.site.each_context(request)
    context['title'] = 'Thanh toán (POS)'
    return render(request, 'admin/pos_embed.html', context)

from booking.views import POSBookingAPIView, POSMasterDataAPIView
urlpatterns = [
    path("api/pos/master-data/", POSMasterDataAPIView.as_view(), name="pos-master"),
    path("api/pos/bookings/", POSBookingAPIView.as_view(), name="pos-bookings"),
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/pos-system/', pos_embed_view, name='pos_embed'),
    path('admin/booking-embed/', admin_booking_embed_view, name='admin_booking_embed'),
    path('admin/', admin.site.urls),
    path('api/', include('booking.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('tinymce/upload/', tinymce_upload, name='tinymce-upload'),
]

admin.site.site_header = "Nha Khoa Minh Sinh"
admin.site.site_title = "Nha Khoa Minh Sinh"
admin.site.index_title = "Bảng điều khiển"

import core.admin

