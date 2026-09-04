from django.urls import path
from .views import SiteSettingsAPIView, ArticleByCategoryUrlView, ArticleDetailView, MenuLinkListAPIView, parse_docx_api, article_detail_api, articles_list_api, ClinicListView, ServiceListView, BookingCreateView, DailyScheduleView, AvailableSlotsView, TopupInfoView, get_services_by_category, get_booking_detail

urlpatterns = [
    path('settings/', SiteSettingsAPIView.as_view(), name='api-settings'),
    path('menus/', MenuLinkListAPIView.as_view(), name='api-menus'),
    path('articles/by-url/', ArticleByCategoryUrlView.as_view(), name='articles-by-url'),
    path('articles/', articles_list_api, name='article-list'),
    path('articles/<slug:slug>/', ArticleDetailView.as_view(), name='article-detail'),
    path('clinics/', ClinicListView.as_view(), name='api-clinics'),
    path('services/', ServiceListView.as_view(), name='api-services'),
    path('bookings/', BookingCreateView.as_view(), name='api-bookings'),
    path('daily-schedule/', DailyScheduleView.as_view(), name='api-daily-schedule'),
    path('available-slots/', AvailableSlotsView.as_view(), name='api-available-slots'),
    path('topup-info/', TopupInfoView.as_view(), name='api-topup-info'),
    path('get-services-by-category/', get_services_by_category, name='get-services-by-category'),
    path('bookings/<int:pk>/detail/', get_booking_detail, name='booking-detail'),
    path('parse-docx/', parse_docx_api, name='parse-docx'),
]
