from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import timedelta
from django.utils.dateparse import parse_datetime, parse_date

from .models import Clinic, ServiceCategory, ServiceDetail, Booking, Customer, BookingStatusHistory, TimeSlot
from .serializers import ClinicSerializer, ServiceCategorySerializer
from django.http import JsonResponse

def get_services_by_category(request):
    category_id = request.GET.get('category_id')
    if not category_id:
        return JsonResponse([], safe=False)
    
    services = ServiceDetail.objects.filter(category_id=category_id).values('service_id', 'name', 'code', 'difficulty', 'price')
    return JsonResponse(list(services), safe=False)

class ClinicListView(generics.ListAPIView):
    def get(self, request):
        clinics = Clinic.objects.all().order_by('clinic_id').values('clinic_id', 'name', 'address', 'hotline', 'total_chairs', 'map_url')
        return Response(list(clinics), status=status.HTTP_200_OK)

class ServiceListView(generics.ListAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer

class DailyScheduleView(APIView):
    def get(self, request):
        clinic_id = request.query_params.get('clinic_id')
        date_str = request.query_params.get('date')
        
        if not clinic_id or not date_str:
            return Response({"error": "Thiếu clinic_id hoặc date"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response({"error": "Không tìm thấy cơ sá»Ÿ"}, status=status.HTTP_404_NOT_FOUND)
            
        target_date = parse_date(date_str)
        if not target_date:
            return Response({"error": "Ngày không hợp lá»‡ (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)
            
        # Lấy tất cả TimeSlots, sắp xếp theo start_time
        time_slots = TimeSlot.objects.all().order_by('start_time')
        
        # Tá»± Ä‘á»™ng khá»Ÿi tạo nếu CSDL chưa có khung giờ nào
        if not time_slots.exists():
            from datetime import time, datetime
            default_times = [
                (time(8,0), time(8,30)), (time(8,30), time(9,0)), (time(9,0), time(9,30)), (time(9,30), time(10,0)),
                (time(14,0), time(14,30)), (time(14,30), time(15,0)), (time(15,0), time(15,30)), (time(15,30), time(16,0))
            ]
            for st, et in default_times:
                TimeSlot.objects.create(start_time=st, end_time=et)
            time_slots = TimeSlot.objects.all().order_by('start_time')
        
        try:
            # Lấy tất cả Bookings trong ngày Ä‘ó của clinic
            bookings = Booking.objects.filter(
                clinic=clinic, 
                start_time__date=target_date,
                status__in=['Pending', 'Confirmed', 'Completed', 'booked', 'paid', 'Booked', 'Paid']
            )
            list(bookings) # Force evaluation to catch DB mismatch errors
        except Exception as e:
            print("DailyScheduleView Booking Error:", e)
            bookings = Booking.objects.none()
        
        
        total_chairs = clinic.total_chairs
        matrix = []
        
        from datetime import datetime, timedelta
        
        # Build booking spans with estimated_duration
        booking_spans = []
        for b in bookings:
            start = timezone.localtime(b.start_time).time() if b.start_time else None
            if not start:
                continue
            duration = b.estimated_duration if b.estimated_duration else 30
            
            dummy = datetime.combine(datetime.today(), start)
            end = (dummy + timedelta(minutes=duration)).time()
            booking_spans.append({"booking": b, "start": start, "end": end, "chair": None})
            
        for ts in time_slots:
            ts_start = ts.start_time
            
            # Find all bookings that are active during this timeslot
            active_bookings = []
            for span in booking_spans:
                if span["start"] <= ts_start < span["end"]:
                    active_bookings.append(span)
                    
            # Assign chairs
            used_chairs = set(span["chair"] for span in active_bookings if span["chair"] is not None)
            for span in active_bookings:
                if span["chair"] is None:
                    for c in range(1, total_chairs + 1):
                        if c not in used_chairs:
                            span["chair"] = c
                            used_chairs.add(c)
                            break
                            
            chairs = []
            for chair_num in range(1, total_chairs + 1):
                active_span = next((s for s in active_bookings if s["chair"] == chair_num), None)
                if active_span:
                    b = active_span["booking"]
                    chairs.append({
                        "chair": chair_num,
                        "status": "booked",
                        "booking_id": b.booking_id,
                        "customer_name": getattr(b.customer, 'name', getattr(b.customer, 'full_name', '')),
                        "service_name": b.category.name if getattr(b, "category", None) else "Chưa chọn dá»‹ch vụ"
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
            return Response({"error": "Không tìm thấy cơ sá»Ÿ"}, status=status.HTTP_404_NOT_FOUND)
            
        target_date = parse_date(date_str)
        
        time_slots = TimeSlot.objects.all().order_by('start_time')
        try:
            bookings = Booking.objects.filter(
                clinic=clinic, 
                start_time__date=target_date,
                status__in=['Pending', 'Confirmed', 'Completed', 'booked', 'paid', 'Booked', 'Paid']
            )
            list(bookings)
        except Exception as e:
            print("AvailableSlotsView Booking Error:", e)
            bookings = Booking.objects.none()
        
        results = []
        for ts in time_slots:
            booked_count = sum(1 for b in bookings if b.start_time and b.end_time and timezone.localtime(b.start_time).time() <= ts.start_time < timezone.localtime(b.end_time).time())
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
        created_user_id = data.get('created_user_id')
        
        if not clinic_id or not date_str or not start_time_str or not patients:
            return Response({"error": "Thiếu dữ liá»‡u Ä‘ầu vào (clinic_id, date, start_time, patients)"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            clinic = Clinic.objects.get(pk=clinic_id)
        except Clinic.DoesNotExist:
            return Response({"error": "Không tìm thấy cơ sá»Ÿ"}, status=status.HTTP_404_NOT_FOUND)
            
        target_date = parse_date(date_str)
        if not target_date:
            return Response({"error": "Äá»‹nh dạng ngày không hợp lá»‡ (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            from datetime import datetime
            start_time = datetime.strptime(start_time_str, "%H:%M").time()
        except ValueError:
            return Response({"error": "Sai Ä‘á»‹nh dạng start_time (HH:MM)"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Tìm sá»‘ lượng booking Ä‘ã có trong ca này
            existing_bookings = Booking.objects.filter(
                clinic=clinic, 
                start_time__date=target_date, 
                status__in=['Pending', 'Confirmed', 'Completed', 'booked', 'paid', 'Booked', 'Paid']
            )
            from datetime import timedelta, datetime as dt_module
            # calculate end_time for the new booking (assuming 30min for now, or use actual)
            # Actually we just want to know if start_time falls into an existing booking
            occupied_count = sum(1 for b in existing_bookings if b.start_time and b.end_time and timezone.localtime(b.start_time).time() <= start_time < timezone.localtime(b.end_time).time())
        except Exception as e:
            print("BookingCreateView Booking Error:", e)
            occupied_count = 0
            
        available_count = max(0, clinic.total_chairs - occupied_count)
        
        if len(patients) > available_count:
            return Response({"error": f"Chá»‰ còn {available_count} ghế trá»‘ng trong khung giờ này!"}, status=status.HTTP_400_BAD_REQUEST)
            
        created_booking_ids = []
        
        from django.db import transaction
        with transaction.atomic():
            for i, p in enumerate(patients):
                full_name = p.get('fullName')
                phone = p.get('phone')
                category_id = p.get('category_id')
                email = p.get('email')
                dob = p.get('dob')
                
                if not full_name or not phone:
                    continue # Bỏ qua khách hàng không có tên/SĐT
                    
                customer, _ = Customer.objects.get_or_create(
                    phone=phone, 
                    defaults={
                        'name': full_name,
                        'email': email,
                        'customer_dob': parse_date(dob) if dob else None
                    }
                )
                
                category = None
                duration_minutes = 30
                if category_id:
                    category = ServiceCategory.objects.filter(pk=category_id).first()
                    if category and category.estimate_time:
                        duration_minutes = category.estimate_time
                        
                from datetime import datetime as dt_module
                appointment_time_dt = dt_module.combine(target_date, start_time)
                from datetime import timedelta
                end_time_dt = appointment_time_dt + timedelta(minutes=duration_minutes)
                
                booking = Booking.objects.create(
                    customer=customer,
                    clinic=clinic,
                    start_time=appointment_time_dt,
                    end_time=end_time_dt,
                    estimated_duration=duration_minutes,
                    status='Pending',
                    category=category,
                    created_user_id=created_user_id
                )
                
                created_booking_ids.append(booking.booking_id)
            
        return JsonResponse({
            "status": "success",
            "booking_id": created_booking_ids[0] if created_booking_ids else None
        }, status=201)

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



from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import localtime
from .models import Booking

def get_booking_detail(request, pk):
    booking = get_object_or_404(Booking, pk=pk)
    return JsonResponse({
        "id": booking.booking_id,
        "customer_name": booking.customer.name if booking.customer else "Khách hàng",
        "clinic_name": booking.clinic.name if booking.clinic else "Nha Khoa Minh Sinh",
        "clinic_address": booking.clinic.address if booking.clinic else "Hồ Chí Minh",
        "category_name": booking.category.name if booking.category else "Dịch vụ nha khoa",
        "start_time": localtime(booking.start_time).strftime("%H:%M - %d/%m/%Y") if booking.start_time else "Chưa xác định",
    })


from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required

@csrf_exempt
@staff_member_required
def parse_docx_api(request):
    if request.method == 'POST' and request.FILES.get('file'):
        uploaded_file = request.FILES['file']
        try:
            import docx
            doc = docx.Document(uploaded_file)
            
            title = ""
            html_content = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                
                if not title:
                    title = text
                    continue
                
                # Basic style conversion
                para_html = ""
                for run in para.runs:
                    run_text = run.text.replace('<', '&lt;').replace('>', '&gt;')
                    if run.bold:
                        para_html += f"<strong>{run_text}</strong>"
                    elif run.italic:
                        para_html += f"<em>{run_text}</em>"
                    else:
                        para_html += run_text
                        
                if para.style.name.startswith('Heading 1'):
                    html_content.append(f"<h1>{para_html}</h1>")
                elif para.style.name.startswith('Heading 2'):
                    html_content.append(f"<h2>{para_html}</h2>")
                elif para.style.name.startswith('Heading 3'):
                    html_content.append(f"<h3>{para_html}</h3>")
                else:
                    html_content.append(f"<p>{para_html}</p>")
            
            content_html = "\n".join(html_content)
            return JsonResponse({'status': 'success', 'title': title, 'content': content_html})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
