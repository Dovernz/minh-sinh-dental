import os
import re
import decimal
from datetime import datetime, date, time, timedelta
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from django.db.models import Q

import openpyxl

# Giả sử các model nằm trong app 'booking' và 'core' hoặc tương đương
# Điều chỉnh import theo cấu trúc thực tế của dự án
from booking.models import Customer, Booking, BookingDetail, Billing, Payment, Clinic, ServiceDetail
from booking.pnr_utils import generate_pnr_code

class Command(BaseCommand):
    help = "Import và đồng bộ dữ liệu Excel tổng hợp 2026 vào Customer, Booking, Billing, Payment"

    def add_arguments(self, parser):
        parser.add_argument('--file', type=str, help='Path to Excel file')
        parser.add_argument('--limit', type=int, default=None, help='Limit rows per sheet for testing')
        parser.add_argument('--dry-run', action='store_true', help='Test parse without committing to DB')

    def handle(self, *args, **options):
        file_path = options['file']
        limit = options['limit']
        dry_run = options['dry_run']

        # 1. Xác định file path
        if not file_path:
            possible_paths = [
                "/app/MINH_SINH_DENTAL_2026.xlsx",
                "/app/MINH SINH DENTAL TỔNG HỢP 2026.xlsx",
                r"D:\Thành\WEB\MINH SINH DENTAL TỔNG HỢP 2026.xlsx"
            ]
            for p in possible_paths:
                if os.path.exists(p):
                    file_path = p
                    break
        
        if not file_path or not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"Không tìm thấy file Excel tại: {file_path}"))
            return

        self.stdout.write(self.style.SUCCESS(f"Bắt đầu xử lý file: {file_path}"))

        # 2. Khởi tạo biến đếm
        self.stats = {
            'customers': 0,
            'bookings': 0,
            'billings': 0,
            'payments': 0,
            'total_revenue': decimal.Decimal('0'),
            'total_debt': decimal.Decimal('0')
        }

        # 3. Mở workbook
        wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        try:
            with transaction.atomic():
                # Xử lý các sheet CRM
                for sheet_name in ['CRM - LB', 'CRM - QS']:
                    if sheet_name in wb.sheetnames:
                        self.process_crm_sheet(wb[sheet_name], sheet_name, limit)
                
                # Xử lý các sheet CÔNG NỢ
                for sheet_name in ['CÔNG NỢ - LB', 'CÔNG NỢ - QS']:
                    if sheet_name in wb.sheetnames:
                        self.process_debt_sheet(wb[sheet_name], sheet_name, limit)

                if dry_run:
                    transaction.set_rollback(True)
                    self.stdout.write(self.style.WARNING("DRY RUN: Đã hoàn tất kiểm tra, không có dữ liệu nào được lưu."))
                else:
                    self.stdout.write(self.style.SUCCESS("Đã lưu dữ liệu vào Database thành công."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Lỗi hệ thống: {str(e)}"))
            import traceback
            traceback.print_exc()
        finally:
            wb.close()

        # 4. In tổng kết
        self.print_summary()

    def get_clinic(self, code):
        """Mapping clinic dựa trên mã LB hoặc QS"""
        if code == 'LB':
            clinic = Clinic.objects.filter(
                Q(name__icontains='Minh Sinh 2') | 
                Q(address__icontains='Long Biên') | 
                Q(address__icontains='Ngọc Lâm')
            ).first()
        else: # QS
            clinic = Clinic.objects.filter(
                Q(name__icontains='Minh Sinh 1') | 
                Q(address__icontains='Quán Sứ') | 
                Q(address__icontains='Hoàn Kiếm')
            ).first()
        
        res = clinic or Clinic.objects.first()
        if not res:
            res = Clinic.objects.create(name=f"Nha khoa Minh Sinh ({code})", total_chairs=5)
        return res

    def clean_phone(self, val, ma_so):
        if val is None:
            return str(ma_so) if ma_so else ""
        s = str(val).strip()
        if not s or s.lower() == 'none':
            return str(ma_so) if ma_so else ""
        # Xử lý số khoa học 9.8E+8
        if 'E+' in s.upper():
            try:
                s = format(float(s), 'f').split('.')[0]
            except:
                pass
        # Xóa .0 ở cuối nếu có
        if s.endswith('.0'):
            s = s[:-2]
        # Chỉ giữ lại số
        s = re.sub(r'\D', '', s)
        if len(s) < 8:
            return str(ma_so) if ma_so else s
        if not s.startswith('0') and len(s) >= 9:
            s = '0' + s
        return s

    def get_safe_phone(self, phone_val, ma_so, ho_ten):
        clean = self.clean_phone(phone_val, ma_so)
        if clean and len(clean) >= 9 and len(clean) <= 12 and clean.isdigit():
            if not Customer.objects.filter(phone=clean).exists():
                return clean
        digits = "".join(filter(str.isdigit, str(ma_so or "")))
        if digits:
            candidate = f"09{digits.zfill(8)}"[:12]
            if not Customer.objects.filter(phone=candidate).exists():
                return candidate
        import hashlib
        h = hashlib.md5(f"{ma_so}_{ho_ten}".encode('utf-8')).hexdigest()
        numeric_h = "".join(filter(str.isdigit, h))[:9].zfill(9)
        candidate = f"09{numeric_h}"[:12]
        if not Customer.objects.filter(phone=candidate).exists():
            return candidate
        import secrets
        return f"09{secrets.token_hex(4)}"[:12]

    def to_decimal(self, val):
        if val is None: return decimal.Decimal('0')
        try:
            # Xử lý chuỗi có dấu phẩy phân cách ngàn
            if isinstance(val, str):
                val = val.replace(',', '').strip()
            return decimal.Decimal(str(val))
        except:
            return decimal.Decimal('0')

    def parse_dob(self, val):
        if val is None: return None
        if isinstance(val, (datetime, date)):
            return val
        try:
            year = int(float(str(val).strip()))
            if 1900 < year < 2100:
                return date(year, 1, 1)
        except:
            pass
        return None

    def parse_datetime(self, val):
        if isinstance(val, datetime):
            return val
        if isinstance(val, date):
            return datetime.combine(val, time(9, 0))
        return timezone.now()

    def process_crm_sheet(self, sheet, sheet_name, limit):
        self.stdout.write(f"Đang xử lý sheet: {sheet_name}")
        clinic_code = 'LB' if 'LB' in sheet_name else 'QS'
        clinic = self.get_clinic(clinic_code)
        
        found_header = False
        count = 0
        for row in sheet.iter_rows(values_only=True):
            if not found_header:
                if row and (row[0] in ['Ngày', 'Mã theo sổ'] or (len(row) > 1 and row[1] == 'Mã theo sổ')):
                    found_header = True
                continue
            
            if limit and count >= limit: break
            if not row or len(row) < 5: continue
            
            # Mapping cột dựa trên yêu cầu
            # 0:ngay, 1:ma_so, 2:co_so, 3:ho_ten, 4:sdt, 5:dia_chi, 6:nam_sinh, 7:gioi_tinh, 8:dich_vu
            # 9:don_gia, 10:ma_giam_gia, 11:gia_sau_giam, 12-17:thuc_thu, 18:cong_no, 19:lich_hen, 20:loai_khach, 21:bsi, 22:notes
            
            ngay_val = row[0]
            ma_so = str(row[1]).strip() if row[1] else None
            ho_ten = str(row[3]).strip() if row[3] else None
            
            if not ho_ten or ho_ten.lower() in ['none', '']:
                continue

            try:
                sdt = self.clean_phone(row[4], ma_so)
                dia_chi = str(row[5]).strip() if row[5] else ""
                dob = self.parse_dob(row[6])
                gioi_tinh = str(row[7]).strip() if row[7] else ""
                dich_vu = str(row[8]).strip() if row[8] else "Khám tư vấn"
                don_gia = self.to_decimal(row[9])
                gia_sau_giam = self.to_decimal(row[11])
                cong_no = self.to_decimal(row[18])
                notes_str = str(row[22]) if len(row) > 22 and row[22] else ""
                
                # 1. Customer
                customer = None
                if sdt and len(sdt) > 7:
                    customer = Customer.objects.filter(phone=sdt).first()
                
                if not customer and ma_so:
                    customer = Customer.objects.filter(Q(patient_code=ma_so) | Q(old_customer_code=ma_so)).first()
                
                if not customer:
                    customer = Customer.objects.filter(name__iexact=ho_ten, address__icontains=dia_chi[:10]).first()

                if customer:
                    if ma_so and not customer.patient_code: customer.patient_code = ma_so
                    if not customer.address: customer.address = dia_chi
                    if dob and not customer.customer_dob: customer.customer_dob = dob
                    customer.save()
                else:
                    safe_phone = self.get_safe_phone(sdt, ma_so, ho_ten)
                    customer = Customer.objects.create(
                        name=ho_ten,
                        phone=safe_phone,
                        patient_code=ma_so,
                        old_customer_code=ma_so,
                        address=dia_chi,
                        gender=gioi_tinh,
                        customer_dob=dob
                    )
                    self.stats['customers'] += 1

                # 2. Service
                service, _ = ServiceDetail.objects.get_or_create(
                    name=dich_vu,
                    defaults={'price': don_gia or 0}
                )

                # 3. Booking
                start_time = self.parse_datetime(ngay_val)
                pnr = generate_pnr_code(prefix="MS")
                status = 'Completed' if cong_no <= 0 and (gia_sau_giam > 0 or don_gia > 0) else 'Confirmed'
                
                booking = Booking.objects.create(
                    customer=customer,
                    clinic=clinic,
                    start_time=start_time,
                    end_time=start_time + timedelta(minutes=30),
                    status=status,
                    pnr_code=pnr,
                    group_code=pnr,
                    notes=notes_str
                )
                self.stats['bookings'] += 1

                # 4. BookingDetail
                BookingDetail.objects.create(
                    booking=booking,
                    service_detail=service,
                    actual_price=don_gia if don_gia > 0 else gia_sau_giam,
                    quantity=1
                )

                # 5. Billing
                final_total = gia_sau_giam if gia_sau_giam > 0 else don_gia
                subtotal = don_gia if don_gia > 0 else gia_sau_giam
                
                # Tính tổng thực thu từ 6 cột (index 12 đến 17)
                payments_amounts = []
                for col_idx in range(12, 18):
                    amt = self.to_decimal(row[col_idx])
                    if amt > 0:
                        payments_amounts.append(amt)
                
                total_paid = sum(payments_amounts)
                if cong_no <= 0 and final_total > 0:
                    b_status = 'PAID'
                elif total_paid > 0:
                    b_status = 'INSTALLMENT'
                else:
                    b_status = 'UNPAID'

                billing = Billing.objects.create(
                    clinic=clinic,
                    booking=booking,
                    subtotal=subtotal,
                    final_total=final_total,
                    status=b_status,
                    notes=notes_str
                )
                self.stats['billings'] += 1
                self.stats['total_revenue'] += total_paid
                self.stats['total_debt'] += cong_no

                # 6. Payments
                current_remain = final_total
                for amt in payments_amounts:
                    current_remain -= amt
                    Payment.objects.create(
                        billing=billing,
                        amount=amt,
                        payment_method='CASH',
                        total_billing=final_total,
                        amount_remain=max(0, current_remain)
                    )
                    self.stats['payments'] += 1

                count += 1
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Lỗi dòng {count+header_row_idx} sheet {sheet_name}: {str(e)}"))
                continue

    def process_debt_sheet(self, sheet, sheet_name, limit):
        self.stdout.write(f"Đang xử lý sheet công nợ: {sheet_name}")
        clinic_code = 'LB' if 'LB' in sheet_name else 'QS'
        clinic = self.get_clinic(clinic_code)

        found_header = False
        count = 0
        for row in sheet.iter_rows(values_only=True):
            if not found_header:
                if row and (row[0] == 'Mã theo sổ' or (len(row) > 1 and row[1] == 'Họ và Tên')):
                    found_header = True
                continue

            if limit and count >= limit: break
            if not row or len(row) < 2 or not row[1]: continue

            ma_so = str(row[0]).strip() if row[0] else None
            ho_ten = str(row[1]).strip()
            hoa_don_goc = self.to_decimal(row[2])
            da_thanh_toan = self.to_decimal(row[3])
            cong_no = self.to_decimal(row[4])

            if cong_no <= 0 and hoa_don_goc <= 0:
                continue

            # Tìm khách hàng
            customer = Customer.objects.filter(Q(patient_code=ma_so) | Q(old_customer_code=ma_so)).first()
            if not customer:
                customer = Customer.objects.filter(name__iexact=ho_ten).first()
            
            if not customer:
                safe_phone = self.get_safe_phone(None, ma_so, ho_ten)
                customer = Customer.objects.create(
                    name=ho_ten,
                    phone=safe_phone,
                    patient_code=ma_so,
                    old_customer_code=ma_so
                )
                self.stats['customers'] += 1

            # Kiểm tra xem đã có billing nào chưa, nếu chưa tạo baseline để ghi nhận nợ
            if not Billing.objects.filter(booking__customer=customer).exists():
                pnr = generate_pnr_code(prefix="DEBT")
                booking = Booking.objects.create(
                    customer=customer,
                    clinic=clinic,
                    start_time=timezone.now(),
                    end_time=timezone.now() + timedelta(minutes=30),
                    status='Confirmed',
                    pnr_code=pnr,
                    group_code=pnr,
                    notes="Dữ liệu công nợ lịch sử từ Excel 2026"
                )
                billing = Billing.objects.create(
                    clinic=clinic,
                    booking=booking,
                    subtotal=hoa_don_goc,
                    final_total=hoa_don_goc,
                    status='INSTALLMENT' if da_thanh_toan > 0 else 'UNPAID',
                    notes="Hóa đơn đối soát công nợ"
                )
                if da_thanh_toan > 0:
                    Payment.objects.create(
                        billing=billing,
                        amount=da_thanh_toan,
                        payment_method='CASH',
                        total_billing=hoa_don_goc,
                        amount_remain=cong_no
                    )
                self.stats['bookings'] += 1
                self.stats['billings'] += 1
            
            count += 1

    def print_summary(self):
        self.stdout.write("\n" + "="*50)
        self.stdout.write(self.style.SUCCESS("KẾT QUẢ IMPORT DỮ LIỆU 2026"))
        self.stdout.write(f"- Khách hàng mới: {self.stats['customers']}")
        self.stdout.write(f"- Lịch hẹn (Booking): {self.stats['bookings']}")
        self.stdout.write(f"- Hóa đơn (Billing): {self.stats['billings']}")
        self.stdout.write(f"- Giao dịch (Payment): {self.stats['payments']}")
        self.stdout.write(f"- Tổng doanh thu thực thu: {self.stats['total_revenue']:,.0f} VNĐ")
        self.stdout.write(f"- Tổng công nợ ghi nhận: {self.stats['total_debt']:,.0f} VNĐ")
        self.stdout.write("="*50 + "\n")