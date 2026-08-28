from django.apps import AppConfig

class BookingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'booking'
    verbose_name = 'Database'

    def ready(self):
        from django.contrib.auth.models import Permission
        
        def custom_permission_str(self):
            # Bóc tách chuỗi "[Quản lý Booking] Can add Lịch Ngày" từ Database
            if self.name.startswith('['):
                parts = self.name.split('] ', 1)
                if len(parts) == 2:
                    group = parts[0].replace('[', '')
                    # Format đầu ra: Quản lý Booking | lịch ngày | Can add Lịch Ngày
                    return f"{group} | {self.content_type.name} | {parts[1]}"
            
            # Trả về mặc định cho các quyền hệ thống khác
            return f"Hệ thống | {self.content_type.name} | {self.name}"
            
        # Ghi đè hàm hiển thị của model Permission trên toàn dự án
        Permission.__str__ = custom_permission_str
