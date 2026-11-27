from django.urls import path
import django.views.generic
from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from .permissions import has_system_user_perm
from .views import SiteSettingsAPIView, ArticleByCategoryUrlView, ArticleDetailView, MenuLinkListAPIView, parse_docx_api, article_detail_api, articles_list_api, ClinicListView, ServiceListView, BookingGroupDetailView, DailyScheduleView, TopupInfoView, get_services_by_category, get_booking_detail, ClinicListAPIView, AdminTimeSlotListView, BookingCompleteView, BookingCancelView, DoctorListView, ServiceTreeAPIView, EmployeeEmbedAPIView, CommissionStatsAPIView, ServiceStatsAPIView, DentalChartViewSet
from .booking_flow_views import AvailableSlotsView, BookingCreateView, BookingDistributionPreviewView

@staff_member_required
def admin_employee_embed_api_view(request):
    if not has_system_user_perm(request.user):
        raise PermissionDenied
    return render(request, 'admin/employee_embed.html')
from .commission_apis import CommissionOverviewAPIView, CommissionDetailAPIView
from .pnr_views import (
    PNRLookupAPIView,
    PNRPaymentAPIView,
    IndividualPaymentAPIView,
    PNRPassengerStatusUpdateAPIView,
    CapacityCheckAPIView
)

urlpatterns = [
    path('pnr/<str:pnr_code>/', PNRLookupAPIView.as_view(), name='api-pnr-lookup'),
    path('pnr/<str:pnr_code>/payment/', PNRPaymentAPIView.as_view(), name='api-pnr-payment'),
    path('pnr/<str:pnr_code>/passenger/<int:booking_id>/update/', PNRPassengerStatusUpdateAPIView.as_view(), name='api-pnr-passenger-update'),
    path('pos/individual-payment/', IndividualPaymentAPIView.as_view(), name='api-pos-individual-payment'),
    path('pos/pnr-payment/', PNRPaymentAPIView.as_view(), name='api-pos-pnr-payment'),
    path('capacity-check/', CapacityCheckAPIView.as_view(), name='api-capacity-check'),
    path('reports/commissions/', CommissionOverviewAPIView.as_view(), name='api-commission-overview'),
    path('reports/commissions/<int:doctor_id>/', CommissionDetailAPIView.as_view(), name='api-commission-detail'),
    path('admin-clinics/', ClinicListAPIView.as_view(), name='api-admin-clinics'),
    path('admin-timeslots/', AdminTimeSlotListView.as_view(), name='api-admin-timeslots'),
    path('settings/', SiteSettingsAPIView.as_view(), name='api-settings'),
    path('menus/', MenuLinkListAPIView.as_view(), name='api-menus'),
    path('articles/by-url/', ArticleByCategoryUrlView.as_view(), name='articles-by-url'),
    path('articles/', articles_list_api, name='article-list'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('clinics/', ClinicListView.as_view(), name='api-clinics'),
    path('services/', ServiceListView.as_view(), name='api-services'),
    path('bookings/', BookingCreateView.as_view(), name='api-bookings'),
    path('bookings/distribute-preview/', BookingDistributionPreviewView.as_view(), name='api-bookings-distribute-preview'),
    path('capacity-distribute/', BookingDistributionPreviewView.as_view(), name='api-capacity-distribute'),
    path('bookings/group/<str:group_code>/', BookingGroupDetailView.as_view(), name='api-booking-group-detail'),
    path('bookings/<int:pk>/complete/', BookingCompleteView.as_view(), name='api-booking-complete'),
    path('booking/<int:pk>/complete/', BookingCompleteView.as_view(), name='api-booking-complete-alias'),
    path('booking/<int:pk>/cancel/', BookingCancelView.as_view(), name='api-booking-cancel'),
    path('daily-schedule/', DailyScheduleView.as_view(), name='api-daily-schedule'),
    path('available-slots/', AvailableSlotsView.as_view(), name='api-available-slots'),
    path('topup-info/', TopupInfoView.as_view(), name='api-topup-info'),
    path('get-services-by-category/', get_services_by_category, name='get-services-by-category'),
    path('bookings/<int:pk>/detail/', get_booking_detail, name='booking-detail'),
    path('parse-docx/', parse_docx_api, name='parse-docx'),
    path('admin-employee-embed/', admin_employee_embed_api_view, name='admin-employee-embed'),
    path('doctors/', DoctorListView.as_view(), name='api-doctors'),
    path('service-tree/', ServiceTreeAPIView.as_view(), name='api-service-tree'),
    path('employees/', EmployeeEmbedAPIView.as_view(), name='api-employees'),
    path('commission-stats/', CommissionStatsAPIView.as_view(), name='api-commission-stats'),
    path('service-stats/', ServiceStatsAPIView.as_view(), name='api-service-stats'),
    path('dental-charts/', DentalChartViewSet.as_view({'get': 'list', 'post': 'create'}), name='api-dental-charts'),
    path('dental-charts/<int:pk>/', DentalChartViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}), name='api-dental-chart-detail'),
]

