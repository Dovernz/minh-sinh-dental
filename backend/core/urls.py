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
from booking.admin_views import admin_pnr_lookup_view


from core.views_sso import sso_to_wordpress_view, sso_login_from_wordpress_view

urlpatterns = [
    # Standalone React Apps hosted directly inside Django (Port 8000)
    path('booking/', xframe_options_exempt(TemplateView.as_view(template_name='booking_standalone.html')), name='booking-standalone'),
    path('booking/success/<str:booking_id>/', xframe_options_exempt(booking_success_view), name='booking-success'),
    path('dental-chart/', xframe_options_exempt(TemplateView.as_view(template_name='dental_chart_standalone.html')), name='dental-chart-standalone'),

    path('admin/pnr-lookup/', admin_pnr_lookup_view, name='admin-pnr-lookup'),
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
    path('admin/sso-login/', sso_login_from_wordpress_view, name='admin-sso-login'),
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
