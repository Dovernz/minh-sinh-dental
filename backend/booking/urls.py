from django.urls import path
from .views import ClinicListView, ServiceListView, BookingCreateView, DailyScheduleView, AvailableSlotsView, TopupInfoView, get_services_by_category

urlpatterns = [
    path('clinics/', ClinicListView.as_view(), name='api-clinics'),
    path('services/', ServiceListView.as_view(), name='api-services'),
    path('bookings/', BookingCreateView.as_view(), name='api-bookings'),
    path('daily-schedule/', DailyScheduleView.as_view(), name='api-daily-schedule'),
    path('available-slots/', AvailableSlotsView.as_view(), name='api-available-slots'),
    path('topup-info/', TopupInfoView.as_view(), name='api-topup-info'),
    path('get-services-by-category/', get_services_by_category, name='get-services-by-category'),
]
