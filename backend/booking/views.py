from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils.dateparse import parse_datetime, parse_date

from .models import Clinic, Service, Booking, Customer, BookingStatus, TimeSlot
from .serializers import ClinicSerializer, ServiceSerializer

class ClinicListView(generics.ListAPIView):
    def get(self, request):
        clinics = Clinic.objects.all().order_by('id').values('id', 'name', 'address', 'hotline', 'total_chairs', 'map_url')
        return Response(list(clinics), status=status.HTTP_200_OK)

class ServiceListView(generics.ListAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class DailyScheduleView(APIView):
    def get(self, request):
        clinic_id = request.query_params.get('clinic_id')
        date_str = request.query_params.get('date')
        
        if not clinic_id or not date_str:
            return Response({"error": "Thiếu clinic_id hoặc date"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response({"error": "Không tìm thấy cơ sở"}, status=status.HTTP_404_NOT_FOUND)
            
        target_date = parse_date(date_str)
        if not target_date:
            return Response({"error": "Ngày không hợp lệ (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Lấy tất cả TimeSlots, sắp xếp theo start_time
        time_slots = TimeSlot.objects.all().order_by('start_time')
        
        # Tự động khởi tạo nếu CSDL chưa có khung giờ nào
        if not time_slots.exists():
            from datetime import time, datetime
            default_times = [
                (time(8,0), time(8,30)), (time(8,30), time(9,0)), (time(9,0), time(9,30)), (time(9,30), time(10,0)),
                (time(14,0), time(14,30)), (time(14,30), time(15,0)), (time(15,0), time(15,30)), (time(15,30), time(16,0))
            ]
            for st, et in default_times:
                TimeSlot.objects.create(start_time=st, end_time=et)
            time_slots = TimeSlot.objects.all().order_by('start_time')
        
        # Lấy tất cả Bookings trong ngày đó của clinic
        bookings = Booking.objects.filter(
            clinic=clinic, 
            booking_date=target_date,
            status_history__status__in=['booked', 'paid', 'Booked', 'Paid']
        ).exclude(status_history__status__iexact='cancelled').distinct()
        
        total_chairs = clinic.total_chairs
        matrix = []
        
        for ts in time_slots:
            ts_bookings = bookings.filter(start_time=ts.start_time)
            chairs = []
            
            for chair_num in range(1, total_chairs + 1):
                # Tìm xem có booking nào đang chiếm ghế này không
                b = ts_bookings.filter(chair_number=chair_num).first()
                if b:
                    chairs.append({
                        "chair": chair_num,
                        "status": "booked",
                        "booking_id": b.id,
                        "customer_name": b.customer.full_name,
                        "service_name": b.service.name if b.service else "Khám tổng quát"
                    })
                else:
                    chairs.append({
                        "chair": chair_num,
                        "status": "available",
                        "booking_id": None,
                        "customer_name": None,
                        "service_name": None
                    })
                    
            matrix.append({
                "time": f"{ts.start_time.strftime('%H:%M')} - {ts.end_time.strftime('%H:%M')}",
                "start_time": ts.start_time.strftime('%H:%M'),
                "chairs": chairs
            })
            
        return Response(matrix, status=status.HTTP_200_OK)

class AvailableSlotsView(APIView):
    def get(self, request):
        clinic_id = request.query_params.get('clinic_id')
        date_str = request.query_params.get('date')
        
        if not clinic_id or not date_str:
            return Response({"error": "Thiếu clinic_id hoặc date"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response({"error": "Không tìm thấy cơ sở"}, status=status.HTTP_404_NOT_FOUND)
            
        target_date = parse_date(date_str)
        
        time_slots = TimeSlot.objects.all().order_by('start_time')
        bookings = Booking.objects.filter(
            clinic=clinic, 
            booking_date=target_date,
            status_history__status__in=['booked', 'paid', 'Booked', 'Paid']
        ).exclude(status_history__status__iexact='cancelled').distinct()
        
        results = []
        for ts in time_slots:
            booked_count = bookings.filter(start_time=ts.start_time).count()
            available = max(0, clinic.total_chairs - booked_count)
            results.append({
                "time": f"{ts.start_time.strftime('%H:%M')} - {ts.end_time.strftime('%H:%M')}",
                "start_time": ts.start_time.strftime('%H:%M'),
                "available_chairs": available
            })
            
        return Response(results, status=status.HTTP_200_OK)

class BookingCreateView(APIView):
    def post(self, request):
        data = request.data
        clinic_id = data.get('clinic_id')
        date_str = data.get('date')
        start_time_str = data.get('start_time')
        patients = data.get('patients', [])
        
        if not clinic_id or not date_str or not start_time_str or not patients:
            return Response({"error": "Thiếu dữ liệu đầu vào (clinic_id, date, start_time, patients)"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response({"error": "Không tìm thấy cơ sở"}, status=status.HTTP_404_NOT_FOUND)
            
        target_date = parse_date(date_str)
        if not target_date:
            return Response({"error": "Định dạng ngày không hợp lệ (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            from datetime import datetime
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
        except ValueError:
            return Response({"error": "Sai định dạng start_time (HH:MM)"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Tìm các ghế trống trong ca này
        existing_bookings = Booking.objects.filter(
            clinic=clinic, 
            booking_date=target_date, 
            start_time=start_time,
            status_history__status__in=['booked', 'paid', 'Booked', 'Paid']
        ).exclude(status_history__status__iexact='cancelled').distinct()
        occupied_chairs = list(existing_bookings.values_list('chair_number', flat=True))
        available_chairs = [c for c in range(1, clinic.total_chairs + 1) if c not in occupied_chairs]
        
        if len(patients) > len(available_chairs):
            return Response({"error": f"Chỉ còn {len(available_chairs)} ghế trống trong khung giờ này!"}, status=status.HTTP_400_BAD_REQUEST)
            
        created_booking_ids = []
        
        from django.db import transaction
        with transaction.atomic():
            for i, p in enumerate(patients):
                full_name = p.get('fullName')
                phone = p.get('phone')
                service_id = p.get('service')
                email = p.get('email')
                dob = p.get('dob')
                
                if not full_name or not phone:
                    continue # Bỏ qua khách hàng không có tên/SĐT
                    
                customer, _ = Customer.objects.get_or_create(
                    phone=phone, 
                    defaults={
                        'full_name': full_name,
                        'email': email,
                        'dob': parse_date(dob) if dob else None
                    }
                )
                
                service = None
                if service_id:
                    service = Service.objects.filter(pk=service_id).first()
                    
                duration = service.duration_minutes if service else 30
                
                from datetime import datetime as dt_module, date
                dummy_dt = dt_module.combine(date.today(), start_time)
                end_time = (dummy_dt + timedelta(minutes=duration)).time()
                
                chair_to_assign = available_chairs[i]
                
                booking = Booking.objects.create(
                    customer=customer,
                    clinic=clinic,
                    service=service,
                    booking_date=target_date,
                    start_time=start_time,
                    end_time=end_time,
                    chair_number=chair_to_assign
                )
                
                BookingStatus.objects.create(booking=booking, status='booked')
                created_booking_ids.append(booking.id)
            
        return Response({
            "message": "Đặt lịch thành công!",
            "booking_ids": created_booking_ids
        }, status=status.HTTP_201_CREATED)

class TopupInfoView(APIView):
    def get(self, request):
        from .models import TopupInfo
        config = TopupInfo.objects.filter(is_default=True).first()
        if not config:
            return Response({'error': 'Chưa cấu hình tài khoản thanh toán'}, status=status.HTTP_404_NOT_FOUND)
            
        amount = request.query_params.get('amount', '0')
        note = request.query_params.get('note', 'Thanh toan')
        
        qr_url = f'https://img.vietqr.io/image/{config.bank_name}-{config.account_number}-compact2.png?amount={amount}&addInfo={note}&accountName={config.account_name}'
        
        return Response({
            'bank_name': config.bank_name,
            'account_number': config.account_number,
            'account_name': config.account_name,
            'qr_url': qr_url
        }, status=status.HTTP_200_OK)
