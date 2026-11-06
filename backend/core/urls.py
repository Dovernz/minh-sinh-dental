from django.views.decorators.clickjacking import xframe_options_exempt
import urllib.parse
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import admin
from django.urls import path, include
from booking.views import tinymce_upload
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from booking.models import Booking

def booking_success_view(request, booking_id):
    import re, urllib.parse
    ids = [x.strip() for x in str(booking_id).split(',') if x.strip() and x.strip() != 'undefined']
    bookings = Booking.objects.select_related('clinic', 'customer', 'category').filter(booking_id__in=ids)
    first_clinic = bookings.first().clinic if bookings.exists() and bookings.first().clinic else None
    
    map_embed_url = ""
    directions_url = ""
    if first_clinic:
        raw_url = (first_clinic.map_url or "").strip()
        # 1. Trích xuất nếu người dùng dán nguyên đoạn <iframe src="...">
        if '<iframe' in raw_url:
            match = re.search(r'src=["\']([^"\']+)["\']', raw_url)
            if match:
                map_embed_url = match.group(1)
        elif 'google.com/maps/embed' in raw_url:
            map_embed_url = raw_url

        # 2. Chuẩn bị query tìm kiếm theo tên và địa chỉ phòng khám
        search_query = f"{first_clinic.name}, {first_clinic.address}" if first_clinic.address else first_clinic.name
        encoded_query = urllib.parse.quote(search_query)

        # 3. Fallback tự động: Dù đổi địa chỉ hay link lỗi, luôn sinh embed chuẩn Google Maps
        if not map_embed_url:
            map_embed_url = f"https://maps.google.com/maps?q={encoded_query}&t=&z=16&ie=UTF8&iwloc=&output=embed"

        # 4. Link mở ứng dụng chỉ đường Google Maps
        if raw_url and not raw_url.startswith('<iframe') and 'embed' not in raw_url:
            directions_url = raw_url
        else:
            directions_url = f"https://www.google.com/maps/search/?api=1&query={encoded_query}"

    return render(request, 'booking_success.html', {
        'booking_id': booking_id,
        'bookings': bookings,
        'clinic': first_clinic,
        'map_embed_url': map_embed_url,
        'directions_url': directions_url,
    })

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

@staff_member_required
def admin_commissions_embed_view(request):
    context = admin.site.each_context(request)
    context['title'] = 'Hoa hồng Bác sĩ'
    return render(request, 'admin/commissions_embed.html', context)

from booking.views import POSBookingAPIView, POSMasterDataAPIView, POSSubmitAPIView, POSConfirmPaymentAPIView, DebtCollectionEmbedView, DebtCollectionRawView, POSDebtListAPIView


import base64
import hashlib
import hmac
import json
import time
from django.conf import settings
from django.http import HttpResponseForbidden, HttpResponseRedirect
from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/login/')
def sso_to_wordpress_view(request):
    user = request.user
    # Kiểm tra quyền linh hoạt qua hệ thống Django Permissions (Grant quyền trực tiếp hoặc qua Group)
    has_perm = (
        user.is_superuser
        or user.has_perm('booking.manage_wordpress_posts')
        or user.has_perm('booking.view_article')
        or user.has_perm('booking.add_article')
        or user.has_perm('booking.change_article')
        or user.has_perm('booking.view_marketingarticle')
    )

    if not has_perm:
        return HttpResponseForbidden(
            """
            <div style="font-family: system-ui, -apple-system, sans-serif; max-width: 520px; margin: 80px auto; padding: 36px; text-align: center; border-radius: 16px; background: #ffffff; box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1); border: 1px solid #fee2e2;">
                <div style="width: 64px; height: 64px; background: #fee2e2; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; font-size: 32px;">
                    🛡️
                </div>
                <h2 style="color: #991b1b; font-size: 20px; font-weight: 700; margin-bottom: 8px;">TRUY CẬP BỊ TỪ CHỐI</h2>
                <p style="color: #4b5563; font-size: 14px; line-height: 1.6; margin-bottom: 24px;">
                    Tài khoản của bạn không có quyền truy cập hệ thống Bài viết & Blog (WordPress).<br>
                    Phân hệ này được bảo mật và <strong>chỉ dành riêng cho Ban Quản Trị (Admin)</strong> và <strong>Bộ phận Marketing</strong>.
                </p>
                <a href="/admin/" style="display: inline-block; padding: 10px 24px; background: #2563eb; color: #ffffff; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 14px; box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);">&larr; Về Bảng điều khiển Quản Trị</a>
            </div>
            """
        )

    wp_role = 'administrator' if user.is_superuser else 'editor'
    target = request.GET.get('target', 'edit.php')

    secret_key = getattr(settings, 'SSO_SECRET_KEY', 'minhsinh_dental_sso_secure_key_2026')
    payload = {
        'u': user.username,
        'e': user.email or f"{user.username}@minhsinh.vn",
        'r': wp_role,
        't': target,
        'exp': int(time.time()) + 60
    }
    raw_payload = json.dumps(payload, separators=(',', ':'))
    b64_payload = base64.urlsafe_b64encode(raw_payload.encode('utf-8')).decode('utf-8').rstrip('=')
    sig = hmac.new(secret_key.encode('utf-8'), b64_payload.encode('utf-8'), hashlib.sha256).hexdigest()
    token = f"{b64_payload}.{sig}"

    return HttpResponseRedirect(f"http://localhost/?minhsinh_sso={token}")

urlpatterns = [
    # Standalone React Apps hosted directly inside Django (Port 8000)
    path('booking/', xframe_options_exempt(TemplateView.as_view(template_name='booking_standalone.html')), name='booking-standalone'),
    path('booking/success/<str:booking_id>/', xframe_options_exempt(booking_success_view), name='booking-success'),
    path('dental-chart/', xframe_options_exempt(TemplateView.as_view(template_name='dental_chart_standalone.html')), name='dental-chart-standalone'),

    path('admin/pos-debt/', DebtCollectionEmbedView.as_view(), name='admin-pos-debt'),
    path('admin/pos-debt-raw/', DebtCollectionRawView.as_view(), name='admin-pos-debt-raw'),
    path('api/pos/debts/', POSDebtListAPIView.as_view(), name='api-pos-debts'),
    path("api/pos/confirm-payment/", POSConfirmPaymentAPIView.as_view(), name="pos-confirm-payment"),
    path("api/pos/submit/", POSSubmitAPIView.as_view(), name="pos-submit"),
    path("api/pos/master-data/", POSMasterDataAPIView.as_view(), name="pos-master"),
    path("api/pos/bookings/", POSBookingAPIView.as_view(), name="pos-bookings"),
    path('admin/password_reset/', auth_views.PasswordResetView.as_view(), name='admin_password_reset'),
    path('admin/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('admin/commissions-embed/', admin_commissions_embed_view, name='admin_commissions_embed'),
    path('admin/pos-system/', pos_embed_view, name='pos_embed'),
    path('admin/booking-embed/', admin_booking_embed_view, name='admin_booking_embed'),
    path('admin/sso-to-wordpress/', sso_to_wordpress_view, name='admin-sso-to-wordpress'),
    path('admin-employee-embed/', TemplateView.as_view(template_name='admin/employee_embed.html'), name='admin-employee-embed'),
    path('admin/', admin.site.urls),
    path('api/', include('booking.urls')),
    path('tinymce/', include('tinymce.urls')),
    path('tinymce/upload/', tinymce_upload, name='tinymce-upload'),
]

admin.site.site_header = "Nha Khoa Minh Sinh"
admin.site.site_title = "Nha Khoa Minh Sinh"
admin.site.index_title = "Bảng điều khiển"

import core.admin
