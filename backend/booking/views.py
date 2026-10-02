from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from django.db.models import Q
from django.conf import settings
from unidecode import unidecode
from django.utils.text import slugify
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
            
        try:
            existing_bookings = Booking.objects.filter(clinic=clinic, start_time__date=target_date, status__in=['Pending', 'Confirmed', 'Completed', 'booked', 'paid', 'Booked', 'Paid'])
            from django.utils import timezone
            occupied_count = sum(1 for b in existing_bookings if b.start_time and b.end_time and timezone.localtime(b.start_time).time() <= start_time < timezone.localtime(b.end_time).time())
        except Exception as e:
            occupied_count = 0
            
        available_count = max(0, clinic.total_chairs - occupied_count)
        
        if len(patients) > available_count:
            return Response({"error": f"Chỉ còn {available_count} ghế trống trong khung giờ này!"}, status=status.HTTP_400_BAD_REQUEST)
            
        created_booking_ids = []
        from django.db import transaction
        with transaction.atomic():
            for p in patients:
                full_name = p.get('fullName')
                phone = p.get('phone')
                category_id = p.get('category_id')
                email = p.get('email')
                dob = p.get('dob')
                
                if not full_name or not phone: continue
                    
                customer, _ = Customer.objects.get_or_create(phone=phone, defaults={'name': full_name, 'email': email, 'customer_dob': parse_date(dob) if dob else None})
                category = ServiceCategory.objects.filter(pk=category_id).first() if category_id else None
                duration_minutes = category.estimate_time if category and category.estimate_time else 30
                        
                from datetime import datetime as dt_module, timedelta
                appointment_time_dt = dt_module.combine(target_date, start_time)
                end_time_dt = appointment_time_dt + timedelta(minutes=duration_minutes)
                
                booking = Booking.objects.create(customer=customer, clinic=clinic, start_time=appointment_time_dt, end_time=end_time_dt, estimated_duration=duration_minutes, status='Pending', category=category, created_user_id=created_user_id)
                created_booking_ids.append(booking.booking_id)

        # ---------------- LOGIC GỬI EMAIL ----------------
        # --- CHẠY NGẦM EMAIL BẰNG THREADING (KHÔNG LÀM LAG TRANG) ---
        def send_async_email(p_list, c_name, c_address, t_str, d_str, map_url=""): 
            try:
                from django.core.mail import send_mail
                from django.conf import settings
                for pat in p_list:
                    p_email = pat.get('email')
                    if p_email:
                        subject = f"Xác nhận Lịch hẹn ngày {d_str} - {c_name}"
                        msg = f'''Xin chào {pat.get('fullName')},

Cảm ơn bạn đã đặt lịch khám.
Thời gian: {t_str} ngày {d_str}.

Trân trọng,'''
                        html_msg = f'''
                        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #e5e7eb; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                            <div style="background-color: #3b82f6; padding: 25px; text-align: center; color: white;">
                                <h2 style="margin: 0; font-size: 24px; font-weight: 800;">Xác Nhận Đặt Lịch!</h2>
                                <p style="margin: 8px 0 0; font-size: 16px; opacity: 0.9;">Nha Khoa Minh Sinh</p>
                            </div>
                            <div style="padding: 30px; color: #374151; line-height: 1.6;">
                                <p style="font-size: 16px;">Xin chào <b style="color: #111827;">{pat.get('fullName')}</b>,</p>
                                <p style="font-size: 15px;">Dưới đây là thông tin chi tiết lịch hẹn của bạn:</p>
                                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 25px 0; border-left: 4px solid #3b82f6; border-right: 1px solid #e2e8f0; border-top: 1px solid #e2e8f0; border-bottom: 1px solid #e2e8f0;">
                                    <p style="margin: 8px 0; font-size: 15px;"><b>👤 Khách hàng:</b> {pat.get('fullName')} - {pat.get('phone')}</p>
                                    <p style="margin: 8px 0; font-size: 15px;"><b>⏰ Thời gian:</b> <span style="color: #b91c1c; font-weight: bold;">{t_str} | Ngày {d_str}</span></p>
                                    <p style="margin: 8px 0; font-size: 15px;"><b>🏥 Cơ sở:</b> {c_name}</p>
                                    <p style="margin: 8px 0; font-size: 15px;"><b>📍 Địa chỉ:</b> {c_address}</p>
                                
                                </div>
                                {f'<div style="text-align: center; margin: 25px 0;"><a href="{map_url}" style="background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; box-shadow: 0 4px 6px rgba(16, 185, 129, 0.2);">📍 Xem Google Map Cơ Sở</a></div>' if map_url else ''}
                                <p style="font-size: 15px;">Vui lòng đến trước 10 phút để được hỗ trợ tốt nhất.</p>
                                <p style="margin: 5px 0 0; font-size: 16px; font-weight: bold; color: #111827;">Đội ngũ Nha Khoa Minh Sinh</p>
                            </div>
                        </div>'''
                        send_mail(subject, msg, getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@minhsinh.com'), [p_email], html_message=html_msg, fail_silently=True)
            except Exception as e:
                print("Thread Email Error:", e)

        import threading
        threading.Thread(target=send_async_email, args=(patients, clinic.name, clinic.address, start_time_str, date_str, getattr(clinic, "map_url", ""))).start()
            
        from django.http import JsonResponse
        return JsonResponse({"status": "success", "booking_id": ",".join(map(str, created_booking_ids)) if created_booking_ids else None}, status=201)

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
    from django.http import JsonResponse
    from .models import Booking
    try:
        booking = Booking.objects.get(pk=pk)
        t_str = "Chưa xác định"
        if booking.start_time:
            try:
                from django.utils.timezone import localtime
                t_str = localtime(booking.start_time).strftime("%H:%M - %d/%m/%Y")
            except:
                t_str = booking.start_time.strftime("%H:%M - %d/%m/%Y")
                
        return JsonResponse({
            "id": booking.booking_id,
            "customer_name": getattr(booking.customer, 'name', 'Khách hàng') if booking.customer else "Khách hàng",
            "clinic_name": getattr(booking.clinic, 'name', 'Nha Khoa') if booking.clinic else "Nha Khoa",
            "clinic_address": getattr(booking.clinic, 'address', '') if booking.clinic else "",
            "category_name": getattr(booking.category, 'name', 'Khám tổng quát') if booking.category else "Khám tổng quát",
            "start_time": t_str,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

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
            clean_title = unidecode(title)
            slug = slugify(clean_title)
            return JsonResponse({'status': 'success', 'title': title, 'slug': slug, 'content': content_html})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader
import traceback

@csrf_exempt
def tinymce_upload(request):
    if request.method == "POST":
        upload_file = request.FILES.get('file')
        if not upload_file:
            return JsonResponse({'error': 'Lỗi: Request không có chứa tệp nào (Missing File)'}, status=400)
        
        try:
            result = cloudinary.uploader.upload(upload_file)
            return JsonResponse({'location': result['secure_url']})
        except Exception as e:
            # IN TOÀN BỘ LỖI RA TERMINAL ĐỂ DEBUG
            print("=== LỖI UPLOAD TINYMCE ===")
            print(traceback.format_exc())
            print("==========================")
            return JsonResponse({'error': f'Server Crash: {str(e)}'}, status=500)
            
    return JsonResponse({'error': 'Sai method'}, status=400)

from django.shortcuts import get_object_or_404
from .models import Article

def article_detail_api(request, slug):
    article = get_object_or_404(Article, slug=slug)
    
    preview_token = request.GET.get('preview')
    
    if hasattr(article, 'status'):
        if article.status == 'Draft':
            # Check if preview token is present
            if preview_token != 'admin_secret_123' and not request.user.is_staff:
                return JsonResponse({'error': 'Not found'}, status=404)
                
    data = {
        'id': article.article_id,
        'title': article.title,
        'slug': article.slug,
        'content': article.content,
        'thumbnail': article.thumbnail.url if getattr(article, 'thumbnail', None) else None,
        'is_draft': getattr(article, 'status', '') == 'Draft',
    }
    return JsonResponse(data)


def articles_list_api(request):
    queryset = Article.objects.filter(status='Published')
    
    category_param = request.GET.get('category')
    if category_param:
        queryset = queryset.filter(category=category_param)
        
    articles_data = []
    for article in queryset:
        articles_data.append({
            'id': article.article_id,
            'title': article.title,
            'slug': article.slug,
            'category': article.category,
            'thumbnail': article.thumbnail.url if article.thumbnail else None,
            # 'created_on': article.created_on.strftime('%d/%m/%Y') if hasattr(article, 'created_on') else ''
        })
    return JsonResponse(articles_data, safe=False)

from .models import SiteSettings, MenuLink
from .serializers import SiteSettingsSerializer, MenuLinkSerializer

class SiteSettingsAPIView(APIView):
    def get(self, request):
        settings = SiteSettings.objects.first()
        if not settings:
            settings = SiteSettings.objects.create()
        serializer = SiteSettingsSerializer(settings)
        return Response(serializer.data)

class MenuLinkListAPIView(generics.ListAPIView):
    queryset = MenuLink.objects.filter(is_active=True, parent__isnull=True).order_by('order')
    serializer_class = MenuLinkSerializer

from rest_framework.views import APIView
from rest_framework.response import Response


from django.http import JsonResponse
from django.views import View

from django.http import JsonResponse
from django.views import View
from booking.models import Article




class ArticleByCategoryUrlView(View):
    def get(self, request):
        try:
            target_url = request.GET.get('url', '').rstrip('/')
            if not target_url: target_url = '/'
                
            from django.db.models import Q
            articles = Article.objects.filter(
                Q(category__url=target_url) | Q(category__url=target_url + '/') |
                Q(category__parent__url=target_url) | Q(category__parent__url=target_url + '/')
            ).order_by('-pk').distinct()
            
            data = []
            for a in articles:
                thumb_url = None
                if getattr(a, 'thumbnail', None):
                    try:
                        url = str(a.thumbnail.url) if hasattr(a.thumbnail, 'url') else str(a.thumbnail)
                        from django.conf import settings
                        thumb_url = f"https://res.cloudinary.com/{getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME', 'ocsxoyvj')}/{url}" if not url.startswith('http') and 'upload' in url else (url if url.startswith('http') else request.build_absolute_uri(url))
                    except Exception: pass
                data.append({"id": a.pk, "title": getattr(a, 'title', ''), "slug": getattr(a, 'slug', str(a.pk)), "thumbnail": thumb_url, "category_name": a.category.title if getattr(a, 'category', None) else ""})
            
            # Khởi tạo Tiêu đề rỗng, truy xuất Database Cấu hình Header
            page_title = ""
            try:
                from booking.models import MenuLink
                menu = MenuLink.objects.filter(Q(url=target_url) | Q(url=target_url + '/')).first()
                if menu: page_title = getattr(menu, 'title', '')
            except Exception: pass
            
            return JsonResponse({"page_title": page_title, "articles": data}, safe=False)
        except Exception as e: return JsonResponse({"error": str(e), "articles": []}, status=500)

class ArticleDetailView(View):
    def get(self, request, slug):
        try:
            article = Article.objects.get(slug=slug)

            # Hàm phụ trợ parse link Cloudinary
            def get_cloud_url(img_obj):
                if not img_obj: return None
                try:
                    url = str(img_obj.url) if hasattr(img_obj, 'url') else str(img_obj)
                    from django.conf import settings
                    return f"https://res.cloudinary.com/{getattr(settings, 'CLOUDINARY_STORAGE', {}).get('CLOUD_NAME', 'ocsxoyvj')}/{url}" if not url.startswith('http') and 'upload' in url else (url if url.startswith('http') else request.build_absolute_uri(url))
                except Exception: return None

            show_banner = getattr(article, 'show_banner', True)
            banner_source = getattr(article, 'banner_image', None) or getattr(article, 'thumbnail', None)

            return JsonResponse({
                "id": article.pk, 
                "title": getattr(article, 'title', ''), 
                "content": getattr(article, 'content', ''), 
                "thumbnail": get_cloud_url(getattr(article, 'thumbnail', None)), 
                "banner_image": get_cloud_url(banner_source) if show_banner else None,
                "show_banner": show_banner,
                "category_name": article.category.title if getattr(article, 'category', None) else ""
            })
        except Exception as e: return JsonResponse({"error": str(e)}, status=404)



from django.views import View
from django.http import JsonResponse

class POSBookingAPIView(View):
    def get(self, request):
        try:
            date_str = request.GET.get('date')
            from datetime import datetime, timedelta, timezone as dt_timezone
            from booking.models import Booking

            if not date_str: 
                # Lấy ngày hiện tại + 7 tiếng để ra chuẩn giờ VN
                date_str = (datetime.now(dt_timezone.utc) + timedelta(hours=7)).strftime('%Y-%m-%d')

            # Tạo mốc 0h và 23h59 theo giờ VN
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
            start_vn = target_date
            end_vn = target_date.replace(hour=23, minute=59, second=59)

            # Trừ 7 tiếng để ép về chuẩn UTC tuyệt đối khi query DB
            start_utc = (start_vn - timedelta(hours=7)).replace(tzinfo=dt_timezone.utc)
            end_utc = (end_vn - timedelta(hours=7)).replace(tzinfo=dt_timezone.utc)

            bookings = Booking.objects.filter(start_time__range=(start_utc, end_utc)).exclude(status__in=['COMPLETED', 'CANCELLED', 'Completed', 'Cancelled', 'Hoàn thành', 'Đã hủy']).select_related('customer')

            data = []
            for b in bookings:
                c = getattr(b, 'customer', None)

                # Ép giờ hiển thị: Cộng 7 tiếng vào start_time của DB
                time_str = '--:--'
                if getattr(b, 'start_time', None):
                    time_str = (b.start_time + timedelta(hours=7)).strftime('%H:%M')

                name = getattr(c, 'name', 'Khách chưa tên') if c else 'Khách chưa tên'
                phone = getattr(c, 'phone', '') if c else ''
                b_id = getattr(b, 'booking_id', getattr(b, 'id', ''))

                data.append({
                    'id': b_id, 
                    'display': f"[{time_str}] {name} - {phone} (ID: {b_id})",
                    'clinic_id': getattr(getattr(b, 'clinic', getattr(b, 'branch', None)), 'clinic_id', getattr(b, 'clinic_id', '')), 'clinic_name': str(getattr(b, 'clinic', getattr(b, 'branch', 'Cơ sở'))), 'customer': {
                        'name': name, 'phone': phone,
                        'gender': getattr(c, 'gender', 'OTHER') if c else 'OTHER',
                        'dob': str(c.customer_dob) if c and getattr(c, 'customer_dob', None) else '',
                        'email': getattr(c, 'email', '') if c else '', 'address': getattr(c, 'address', '') if c else ''
                    }
                })
            return JsonResponse({'bookings': data})
        except Exception as e: 
            return JsonResponse({'error': str(e)}, status=500)

class POSMasterDataAPIView(View):
    def get(self, request):
        try:
            from booking.models import Clinic, TopupInfo, ServiceCategory, ServiceDetail, Employee, Discount
            
            categories = list(ServiceCategory.objects.values('category_id', 'name'))
            services = list(ServiceDetail.objects.values('service_id', 'name', 'price', 'category_id'))
            
            doctors = list(Employee.objects.filter(role='Doctor').values('employee_id', 'full_name'))
            
            discounts = []
            for d in Discount.objects.filter(is_active=True):
                discounts.append({
                    'id': d.discount_id, 'code': d.code, 
                    'type': d.discount_type, 
                    'value': float(getattr(d, 'value', 0)), 'desc': getattr(d, 'description', '')
                })
                
            
            clinics = [{'id': c.clinic_id, 'name': c.name} for c in Clinic.objects.all()]
            bank_info = {}
            topup = TopupInfo.objects.filter(is_default=True).first()
            if not topup: topup = TopupInfo.objects.first()
            if topup:
                b_code = getattr(topup, 'bank_name', 'MB')
                a_no = getattr(topup, 'account_number', '')
                a_name = getattr(topup, 'account_name', '')
                bank_info = {'bank_code': b_code, 'account_number': a_no, 'account_name': a_name}

            return JsonResponse({'clinics': clinics, 'categories': categories, 'services': services, 'doctors': doctors, 'discounts': discounts, 'bank_info': bank_info})
        except Exception as e: return JsonResponse({'error': str(e)}, status=500)


from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction

@method_decorator(csrf_exempt, name='dispatch')
class POSSubmitAPIView(View):
    def post(self, request):
        try:
            import json
            data = json.loads(request.body)
            from booking.models import Booking, Customer, BookingDetail, Billing, Clinic
            from datetime import datetime
            from django.db import transaction
            
            with transaction.atomic():
                cust_data = data.get('customer', {})
                if data.get('booking_id'):
                    booking = Booking.objects.get(booking_id=data['booking_id'])
                    customer = booking.customer
                    if customer:
                        customer.name = cust_data.get('name', customer.name)
                        customer.phone = cust_data.get('phone', customer.phone)
                        customer.gender = cust_data.get('gender', customer.gender)
                        customer.email = cust_data.get('email', customer.email)
                        customer.address = cust_data.get('address', customer.address)
                        if cust_data.get('dob'): customer.customer_dob = cust_data['dob']
                        customer.save()
                else:
                    customer = Customer.objects.create(
                        name=cust_data.get('name', 'Khách Vãng Lai'), phone=cust_data.get('phone', ''),
                        gender=cust_data.get('gender', 'OTHER'), email=cust_data.get('email', ''), address=cust_data.get('address', '')
                    )
                    if cust_data.get('dob'):
                        customer.customer_dob = cust_data['dob']
                        customer.save()
                    booking = Booking.objects.create(
                        customer=customer, clinic=Clinic.objects.filter(clinic_id=data.get('clinic_id')).first() if data.get('clinic_id') else Clinic.objects.first(),
                        start_time=datetime.now(), status='Completed', notes="Khách vãng lai POS"
                    )
                
                booking.status = 'Completed'
                booking.save()

                billing_data = data.get('billing', {})
                billing = Billing.objects.create(
                    booking=booking,
                    subtotal=billing_data.get('subtotal', 0),
                    discount_id=billing_data.get('discount_id') or None,
                    adjustment=billing_data.get('adjustment', 0),
                    final_total=billing_data.get('final_total', 0),
                    payment_method=billing_data.get('payment_method', 'CASH'),
                    clinic=booking.clinic,
                    status='UNPAID'
                )

                BookingDetail.objects.filter(booking=booking).delete()
                for srv in data.get('services', []):
                    if srv.get('service_id'):
                        BookingDetail.objects.create(
                            booking=booking, service_detail_id=srv['service_id'], doctor_id=srv.get('doctor_id') or None,
                            tooth_position=srv.get('tooth', ''), quantity=1, actual_price=srv.get('price', 0)
                        )
            return JsonResponse({'status': 'success', 'booking_id': booking.booking_id, 'billing_id': billing.billing_id})
        except Exception as e: 
            return JsonResponse({'error': str(e)}, status=400)



@method_decorator(csrf_exempt, name='dispatch')
class POSConfirmPaymentAPIView(View):
    def post(self, request):
        try:
            import json
            from django.db.models import Sum
            from booking.models import Billing, Payment
            from django.db import transaction
            
            data = json.loads(request.body)
            pay_amount = float(data.get('amount', 0))
            
            with transaction.atomic():
                billing = Billing.objects.get(billing_id=data.get('billing_id'))
                
                prev_payments = Payment.objects.filter(billing=billing).aggregate(Sum('amount'))['amount__sum'] or 0
                
                total = float(billing.final_total)
                remain = total - float(prev_payments) - pay_amount
                if remain < 0: remain = 0
                
                Payment.objects.create(
                    billing=billing,
                    amount=pay_amount,
                    payment_method=data.get('payment_method', 'CASH'),
                    total_billing=total,
                    amount_remain=remain
                )
                
                billing.status = 'PAID' if remain <= 0 else 'INSTALLMENT'
                billing.save()
                
            return JsonResponse({'status': 'success', 'remain': remain, 'bill_status': billing.status})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)


from django.views.generic import TemplateView
from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt


class DebtCollectionEmbedView(TemplateView):
    template_name = 'admin/debt_collection_embed.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib import admin
        # Bơm toàn bộ dữ liệu menu, user, giao diện của Admin vào trang hiện tại
        context.update(admin.site.each_context(self.request))
        context['title'] = 'Thu hồi Công nợ'  # Đổi Tiêu đề tab Trình duyệt
        context['content_title'] = 'Quản lý Thu hồi Công nợ'
        return context

@method_decorator(xframe_options_exempt, name='dispatch')
class DebtCollectionRawView(TemplateView):
    template_name = 'admin/debt_collection_raw.html' 

class POSDebtListAPIView(View):
    def get(self, request):
        try:
            from booking.models import Billing
            from django.db.models import Sum
            
            debts = Billing.objects.filter(status__in=['UNPAID', 'INSTALLMENT']).select_related('booking__customer', 'clinic').order_by('created_at')
            data = []
            for b in debts:
                paid_sum = b.payments.aggregate(Sum('amount'))['amount__sum'] or 0
                remain = float(b.final_total or 0) - float(paid_sum)
                if remain > 0:
                    data.append({
                        'id': b.billing_id,
                        'customer_name': getattr(b.booking.customer, 'name', 'Khách Vãng Lai') if (b.booking and b.booking.customer) else 'Khách Vãng Lai',
                        'phone': getattr(b.booking.customer, 'phone', '') if (b.booking and b.booking.customer) else '',
                        'clinic_name': getattr(b.clinic, 'name', 'Trụ sở chính') if b.clinic else 'Trụ sở chính',
                        'final_total': float(b.final_total or 0),
                        'paid_amount': float(paid_sum),
                        'remain_amount': remain
                    })
            return JsonResponse({'status': 'success', 'debts': data})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class ClinicListAPIView(View):
    def get(self, request):
        try:
            from booking.models import Clinic
            clinics = Clinic.objects.all().values('clinic_id', 'name')
            return JsonResponse({'status': 'success', 'clinics': list(clinics)})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class AdminTimeSlotListView(APIView):
    def get(self, request):
        from .models import TimeSlot
        slots = TimeSlot.objects.all().order_by('start_time')
        data = [
            {
                'id': slot.timeslot_id,
                'start_time': slot.start_time.strftime('%H:%M') if slot.start_time else None,
                'end_time': slot.end_time.strftime('%H:%M') if slot.end_time else None
            } for slot in slots
        ]
        return Response(data, status=status.HTTP_200_OK)

class BookingCompleteView(APIView):
    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy booking"}, status=status.HTTP_404_NOT_FOUND)
        
        booking.status = 'Completed'
        booking.save(update_fields=['status'])
        
        return Response({"message": "Booking completed successfully", "id": pk}, status=status.HTTP_200_OK)

class BookingCancelView(APIView):
    def post(self, request, pk):
        try:
            booking = Booking.objects.get(pk=pk)
        except Booking.DoesNotExist:
            return Response({"error": "Không tìm thấy booking"}, status=status.HTTP_404_NOT_FOUND)
        
        booking.status = 'Cancelled'
        booking.save(update_fields=['status'])
        
        return Response({"message": "Booking cancelled successfully", "id": pk}, status=status.HTTP_200_OK)

class DoctorListView(View):
    def get(self, request):
        from booking.models import Employee
        doctors = Employee.objects.filter(role='Doctor').values('employee_id', 'full_name', 'contract_type')
        return JsonResponse(list(doctors), safe=False)

class ServiceTreeAPIView(View):
    def get(self, request):
        from booking.models import ServiceCategory
        categories = ServiceCategory.objects.prefetch_related('services').all()
        data = []
        for cat in categories:
            services = [{'service_id': s.service_id, 'name': s.name, 'base_price': s.price} for s in cat.services.all()]
            data.append({
                'category_id': cat.category_id,
                'name': cat.name,
                'services': services
            })
        return JsonResponse(data, safe=False)

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json

@method_decorator(csrf_exempt, name='dispatch')
class EmployeeEmbedAPIView(View):
    def get(self, request):
        from booking.models import Employee
        emp_id = request.GET.get('employee_id')
        if emp_id:
            try:
                emp = Employee.objects.get(pk=emp_id)
                return JsonResponse({'employee_id': emp.employee_id, 'full_name': emp.full_name, 'contract_type': emp.contract_type, 'role': emp.role})
            except Employee.DoesNotExist:
                return JsonResponse({'error': 'Not found'}, status=404)
        emps = Employee.objects.all().values('employee_id', 'full_name', 'contract_type', 'role')
        return JsonResponse(list(emps), safe=False)

    def post(self, request):
        from booking.models import Employee
        data = json.loads(request.body)
        emp = Employee.objects.create(
            full_name=data.get('full_name'),
            contract_type=data.get('contract_type', 'Full-time'),
            role=data.get('role', 'Doctor')
        )
        return JsonResponse({'status': 'success', 'employee_id': emp.employee_id})

    def put(self, request):
        from booking.models import Employee
        data = json.loads(request.body)
        try:
            emp = Employee.objects.get(pk=data.get('employee_id'))
            emp.full_name = data.get('full_name', emp.full_name)
            emp.phone = data.get('phone', emp.phone)
            emp.email = data.get('email', emp.email)
            emp.dob = data.get('dob') or emp.dob
            emp.company_email = data.get('company_email', emp.company_email)
            emp.nickname = data.get('nickname', emp.nickname)
            emp.department = data.get('department', emp.department)
            emp.is_all_clinics = data.get('is_all_clinics', emp.is_all_clinics)
            emp.clinic_id = data.get('clinic_id', emp.clinic_id)
            emp.specialty = data.get('specialty', emp.specialty)
            emp.allowance_position = data.get('allowance_position', emp.allowance_position)
            emp.allowance_degree = data.get('allowance_degree', emp.allowance_degree)
            emp.allowance_specialty = data.get('allowance_specialty', emp.allowance_specialty)
            emp.annual_leave_days = data.get('annual_leave_days', emp.annual_leave_days)
            emp.used_leave_days = data.get('used_leave_days', emp.used_leave_days)
            emp.start_date = data.get('start_date', emp.start_date)
            emp.base_salary = data.get('base_salary', emp.base_salary)
            emp.agreed_salary = data.get('agreed_salary', emp.agreed_salary)
            emp.contract_type = data.get('contract_type', emp.contract_type)
            emp.role = data.get('role', emp.role)
            emp.save()
            return JsonResponse({'status': 'success'})
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

    def delete(self, request):
        from booking.models import Employee
        data = json.loads(request.body)
        try:
            emp = Employee.objects.get(pk=data.get('employee_id'))
            emp.delete()
            return JsonResponse({'status': 'success'})
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)

class CommissionStatsAPIView(View):
    def get(self, request):
        from booking.models import BookingDetail
        details = BookingDetail.objects.filter(booking__status='Completed')
        data = []
        for d in details:
            if d.consulting_doctor:
                data.append({
                    'doctor': d.consulting_doctor.full_name,
                    'type': 'Consulting',
                    'commission': float(d.consulting_commission)
                })
            if d.performing_doctor:
                data.append({
                    'doctor': d.performing_doctor.full_name,
                    'type': 'Performing',
                    'commission': float(d.performing_commission)
                })
        return JsonResponse(data, safe=False)

class ServiceStatsAPIView(View):
    def get(self, request):
        from booking.models import BookingDetail
        from django.db.models import Sum
        stats = BookingDetail.objects.filter(booking__status='Completed').values('service_detail__name').annotate(total=Sum('quantity'))
        return JsonResponse(list(stats), safe=False)


from rest_framework import viewsets
from .models import DentalChart
from .serializers import DentalChartSerializer
from django.db.models import Max

class DentalChartViewSet(viewsets.ModelViewSet):
    serializer_class = DentalChartSerializer
    
    def get_queryset(self):
        customer_id = self.request.query_params.get('customer_id')
        qs = DentalChart.objects.all()
        if customer_id:
            qs = qs.filter(customer_id=customer_id)
        return qs.order_by('-sequence_num')

    def perform_create(self, serializer):
        customer = serializer.validated_data.get('customer')
        max_seq = DentalChart.objects.filter(customer=customer).aggregate(Max('sequence_num'))['sequence_num__max']
        next_seq = (max_seq or 0) + 1
        serializer.save(sequence_num=next_seq)



