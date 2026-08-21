from django.core.management.base import BaseCommand
from datetime import time, datetime, timedelta
from booking.models import TimeSlot

class Command(BaseCommand):
    help = 'Tự động tạo các TimeSlots cách nhau 30 phút từ 08:00 đến 17:00'

    def handle(self, *args, **kwargs):
        start_time = time(8, 0)
        end_time_limit = time(17, 0)
        
        dummy_date = datetime.today()
        current_dt = datetime.combine(dummy_date, start_time)
        end_dt = datetime.combine(dummy_date, end_time_limit)
        
        created_count = 0
        while current_dt < end_dt:
            st = current_dt.time()
            current_dt += timedelta(minutes=30)
            et = current_dt.time()
            
            # Tạo hoặc lấy TimeSlot nếu đã tồn tại
            obj, created = TimeSlot.objects.get_or_create(
                start_time=st,
                defaults={'end_time': et}
            )
            if created:
                created_count += 1
                
        self.stdout.write(self.style.SUCCESS(f'Đã tạo thành công {created_count} khung giờ mới!'))
