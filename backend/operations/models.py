from django.db import models
from booking.models import Booking
from django.contrib import admin
from django.db.models import Sum

class ManageBooking(Booking):
    class Meta:
        proxy = True
        verbose_name = 'Chi tiết Bookings'
        verbose_name_plural = 'Chi tiết Bookings'

    @admin.display(description='Trạng thái hiện tại')
    def current_status(self):
        latest = self.status_history.order_by('-created_at').first()
        return latest.status if latest else 'Chưa có'

    @admin.display(description='Đã thu')
    def total_paid(self):
        total = self.payments.aggregate(total_sum=Sum('amount'))['total_sum']
        return total if total is not None else 0

class DailySchedule(Booking):
    class Meta:
        proxy = True
        verbose_name = 'Lịch Ngày'
        verbose_name_plural = 'Lịch Ngày'

class WeeklySchedule(Booking):
    class Meta:
        proxy = True
        verbose_name = 'Lịch Tuần'
        verbose_name_plural = 'Lịch Tuần'
