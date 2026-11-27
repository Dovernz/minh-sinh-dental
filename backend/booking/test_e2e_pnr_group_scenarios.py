import zoneinfo
from decimal import Decimal
from datetime import datetime, timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from django.contrib.auth.models import User, Group
from booking.models import (
    Clinic, Customer, ServiceCategory, ServiceDetail,
    Booking, BookingDetail, Billing, Payment
)

vn_tz = zoneinfo.ZoneInfo('Asia/Ho_Chi_Minh')

class PNRGroupE2ETestCase(APITestCase):
    fixtures = ['rbac_roles.json']

    """
    E2E Test Suite for Dental PNR Group Booking System:
    - Case 1: Multi-Customer Booking & PNR Lookup
    - Case 2: Individual / Split Payment
    - Case 3: Full Group Payment
    - Case 4: Partial Cancellation & Capacity Release
    """

    def setUp(self):
        self.reception_user = User.objects.create_user(username='e2e_reception', is_staff=True)
        self.reception_user.groups.add(Group.objects.get(name='Reception'))
        self.client.force_authenticate(user=self.reception_user)

        # 1. Cơ sở phòng khám test
        self.clinic = Clinic.objects.create(
            name="Nha Khoa Minh Sinh - Luxury PNR Center",
            address="123 Tran Duy Hung, Ha Noi",
            total_chairs=5
        )

        # 2. Danh mục & Dịch vụ với các mức giá khác nhau
        self.cat_kham = ServiceCategory.objects.create(name="Khám & Chẩn đoán", estimate_time=30)
        self.cat_nha_chu = ServiceCategory.objects.create(name="Nha chu", estimate_time=30)
        self.cat_nho_rang = ServiceCategory.objects.create(name="Tiểu phẫu răng", estimate_time=45)
        self.cat_tham_my = ServiceCategory.objects.create(name="Nha khoa thẩm mỹ", estimate_time=60)

        self.svc_lay_cao = ServiceDetail.objects.create(category=self.cat_nha_chu, name="Lấy cao răng siêu âm", code="NH01", price=300000)
        self.svc_han_rang = ServiceDetail.objects.create(category=self.cat_nha_chu, name="Hàn răng Composite", code="NH02", price=500000)
        self.svc_nho_rang = ServiceDetail.objects.create(category=self.cat_nho_rang, name="Nhổ răng khôn số 8", code="TP01", price=1200000)
        self.svc_tay_trang = ServiceDetail.objects.create(category=self.cat_tham_my, name="Tẩy trắng răng Laser", code="TM01", price=2000000)

    def test_case_1_multi_customer_booking_and_pnr_lookup(self):
        """
        Case 1: Multi-Customer Booking & PNR Lookup
        - Nhóm 4 khách kèm đơn giá riêng từng dịch vụ:
          + Khách 1: Lấy cao răng (300,000đ) lúc 09:00
          + Khách 2: Hàn răng Composite (500,000đ) lúc 09:30
          + Khách 3: Nhổ răng khôn (1,200,000đ) lúc 10:00
          + Khách 4: Tẩy trắng răng (2,000,000đ) lúc 10:30
        - Tra cứu PNR -> Khớp 4 khách, đúng giờ khám, đơn giá riêng, tổng tiền = 4,000,000đ.
        """
        pnr_code = "MSGRP1"
        target_date = datetime(2026, 12, 1, tzinfo=vn_tz)

        customers_data = [
            ("Khách Hàng A", "0901000001", "09:00", 30, self.svc_lay_cao, 300000),
            ("Khách Hàng B", "0901000002", "09:30", 30, self.svc_han_rang, 500000),
            ("Khách Hàng C", "0901000003", "10:00", 45, self.svc_nho_rang, 1200000),
            ("Khách Hàng D", "0901000004", "10:30", 60, self.svc_tay_trang, 2000000),
        ]

        bookings = []
        for name, phone, t_str, dur, svc, price in customers_data:
            cust = Customer.objects.create(name=name, phone=phone)
            t_hour, t_min = map(int, t_str.split(':'))
            st = target_date.replace(hour=t_hour, minute=t_min)
            et = st + timedelta(minutes=dur)

            b = Booking.objects.create(
                customer=cust,
                clinic=self.clinic,
                pnr_code=pnr_code,
                group_code=pnr_code,
                start_time=st,
                end_time=et,
                estimated_duration=dur,
                status='Confirmed'
            )
            BookingDetail.objects.create(
                booking=b,
                service_detail=svc,
                actual_price=price,
                quantity=1
            )
            Billing.objects.create(
                booking=b,
                clinic=self.clinic,
                subtotal=price,
                final_total=price,
                status='UNPAID'
            )
            bookings.append(b)

        # Tra cứu thông qua API Endpoint PNR Lookup: /api/pnr/<pnr_code>/
        response = self.client.get(f'/api/pnr/{pnr_code}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        # 1. Kiểm tra thông tin chung PNR
        self.assertEqual(data['pnr_code'], pnr_code)
        self.assertEqual(data['total_passengers'], 4)
        self.assertEqual(data['total_amount'], 4000000.0)
        self.assertEqual(data['total_paid'], 0.0)
        self.assertEqual(data['remaining_balance'], 4000000.0)
        self.assertEqual(data['payment_status'], 'UNPAID')

        # 2. Kiểm tra thông tin từng khách hàng
        passengers = data['passengers']
        self.assertEqual(len(passengers), 4)

        for i, (name, phone, t_str, dur, svc, price) in enumerate(customers_data):
            p = passengers[i]
            self.assertEqual(p['customer']['name'], name)
            self.assertEqual(p['customer']['phone'], phone)
            self.assertIn(t_str, p['start_time'])
            self.assertEqual(p['individual_amount'], float(price))
            self.assertEqual(p['individual_paid'], 0.0)
            self.assertEqual(p['individual_balance'], float(price))
            self.assertEqual(p['billing_status'], 'UNPAID')
            self.assertEqual(len(p['services']), 1)
            self.assertEqual(p['services'][0]['name'], svc.name)
            self.assertEqual(p['services'][0]['price'], float(price))

        print("\n[PASS] Case 1: Multi-Customer Booking & PNR Lookup - Khớp toàn bộ 4 khách, giờ khám, dịch vụ, đơn giá lẻ & tổng thu 4,000,000đ.")

    def test_case_2_individual_split_payment(self):
        """
        Case 2: Individual / Split Payment
        - Nhóm 4 khách ban đầu tổng 4,000,000đ (A: 300k, B: 500k, C: 1200k, D: 2000k).
        - Thực hiện thanh toán lẻ:
          + Khách A trả 300,000đ qua POS Individual Payment API.
          + Khách B trả 500,000đ qua POS Individual Payment API.
        - Kết quả kiểm tra:
          + Khách A, B: billing status = 'PAID', Booking status = 'Completed'.
          + Khách C, D: billing status = 'UNPAID'.
          + PNR: payment_status = 'PARTIAL'.
          + Tiền đã thu = 800,000đ, Nợ còn lại = 3,200,000đ.
        """
        pnr_code = "MSGRP2"
        target_date = datetime(2026, 12, 1, tzinfo=vn_tz)

        customers_data = [
            ("Khách A", "0902000001", "09:00", self.svc_lay_cao, 300000),
            ("Khách B", "0902000002", "09:30", self.svc_han_rang, 500000),
            ("Khách C", "0902000003", "10:00", self.svc_nho_rang, 1200000),
            ("Khách D", "0902000004", "10:30", self.svc_tay_trang, 2000000),
        ]

        created_bookings = []
        for name, phone, t_str, svc, price in customers_data:
            cust = Customer.objects.create(name=name, phone=phone)
            t_hour, t_min = map(int, t_str.split(':'))
            st = target_date.replace(hour=t_hour, minute=t_min)
            et = st + timedelta(minutes=30)

            b = Booking.objects.create(
                customer=cust, clinic=self.clinic,
                pnr_code=pnr_code, group_code=pnr_code,
                start_time=st, end_time=et, status='Confirmed'
            )
            BookingDetail.objects.create(booking=b, service_detail=svc, actual_price=price, quantity=1)
            Billing.objects.create(booking=b, clinic=self.clinic, subtotal=price, final_total=price, status='UNPAID')
            created_bookings.append(b)

        bA, bB, bC, bD = created_bookings

        # 1. Thanh toán lẻ Khách A: 300,000đ
        res_pay_A = self.client.post('/api/pos/individual-payment/', {
            "booking_id": bA.booking_id,
            "amount": 300000,
            "payment_method": "QR"
        }, format='json')
        self.assertEqual(res_pay_A.status_code, status.HTTP_200_OK)

        # 2. Thanh toán lẻ Khách B: 500,000đ
        res_pay_B = self.client.post('/api/pos/individual-payment/', {
            "booking_id": bB.booking_id,
            "amount": 500000,
            "payment_method": "CASH"
        }, format='json')
        self.assertEqual(res_pay_B.status_code, status.HTTP_200_OK)

        # 3. Tra cứu PNR sau khi thanh toán lẻ
        res_lookup = self.client.get(f'/api/pnr/{pnr_code}/')
        self.assertEqual(res_lookup.status_code, status.HTTP_200_OK)
        data = res_lookup.data

        # Kiểm tra trạng thái tài chính của PNR
        self.assertEqual(data['payment_status'], 'PARTIAL')
        self.assertEqual(data['total_amount'], 4000000.0)
        self.assertEqual(data['total_paid'], 800000.0)
        self.assertEqual(data['remaining_balance'], 3200000.0)

        # Kiểm tra chi tiết từng khách
        passengers = {p['customer']['name']: p for p in data['passengers']}
        self.assertEqual(passengers['Khách A']['billing_status'], 'PAID')
        self.assertEqual(passengers['Khách A']['individual_paid'], 300000.0)
        self.assertEqual(passengers['Khách A']['individual_balance'], 0.0)

        self.assertEqual(passengers['Khách B']['billing_status'], 'PAID')
        self.assertEqual(passengers['Khách B']['individual_paid'], 500000.0)
        self.assertEqual(passengers['Khách B']['individual_balance'], 0.0)

        self.assertEqual(passengers['Khách C']['billing_status'], 'UNPAID')
        self.assertEqual(passengers['Khách C']['individual_paid'], 0.0)
        self.assertEqual(passengers['Khách C']['individual_balance'], 1200000.0)

        self.assertEqual(passengers['Khách D']['billing_status'], 'UNPAID')
        self.assertEqual(passengers['Khách D']['individual_paid'], 0.0)
        self.assertEqual(passengers['Khách D']['individual_balance'], 2000000.0)

        print("\n[PASS] Case 2: Individual / Split Payment - A & B PAID, C & D UNPAID, PNR trạng thái PARTIAL, đã thu 800k, nợ 3,200k chuẩn xác.")

    def test_case_3_full_group_payment(self):
        """
        Case 3: Full Group Payment
        - Nhóm 4 khách (A: 300k, B: 500k, C: 1200k, D: 2000k, tổng = 4,000,000đ).
        - Thực hiện thanh toán gộp toàn bộ PNR với 1 lệnh thanh toán 4,000,000đ qua /api/pnr/<pnr>/payment/.
        - Kết quả kiểm tra:
          + Toàn bộ khách A, B, C, D đều chuyển sang billing status 'PAID' và booking status 'Completed'.
          + PNR: payment_status = 'PAID'.
          + Dư nợ còn lại = 0.
          + Group status = 'COMPLETED'.
        """
        pnr_code = "MSGRP3"
        target_date = datetime(2026, 12, 1, tzinfo=vn_tz)

        customers_data = [
            ("Khách G1", "0903000001", "09:00", self.svc_lay_cao, 300000),
            ("Khách G2", "0903000002", "09:30", self.svc_han_rang, 500000),
            ("Khách G3", "0903000003", "10:00", self.svc_nho_rang, 1200000),
            ("Khách G4", "0903000004", "10:30", self.svc_tay_trang, 2000000),
        ]

        created_bookings = []
        for name, phone, t_str, svc, price in customers_data:
            cust = Customer.objects.create(name=name, phone=phone)
            t_hour, t_min = map(int, t_str.split(':'))
            st = target_date.replace(hour=t_hour, minute=t_min)
            et = st + timedelta(minutes=30)

            b = Booking.objects.create(
                customer=cust, clinic=self.clinic,
                pnr_code=pnr_code, group_code=pnr_code,
                start_time=st, end_time=et, status='Confirmed'
            )
            BookingDetail.objects.create(booking=b, service_detail=svc, actual_price=price, quantity=1)
            Billing.objects.create(booking=b, clinic=self.clinic, subtotal=price, final_total=price, status='UNPAID')
            created_bookings.append(b)

        # 1. Thanh toán gộp 4,000,000đ cho cả đoàn
        pay_res = self.client.post(f'/api/pnr/{pnr_code}/payment/', {
            "amount": 4000000,
            "payment_method": "QR",
            "notes": "Thanh toán gộp toàn bộ đoàn qua mã QR"
        }, format='json')
        self.assertEqual(pay_res.status_code, status.HTTP_200_OK)
        self.assertEqual(pay_res.data['remaining_balance'], 0.0)

        # 2. Tra cứu PNR sau khi thanh toán toàn bộ
        lookup_res = self.client.get(f'/api/pnr/{pnr_code}/')
        self.assertEqual(lookup_res.status_code, status.HTTP_200_OK)
        data = lookup_res.data

        self.assertEqual(data['payment_status'], 'PAID')
        self.assertEqual(data['group_status'], 'COMPLETED')
        self.assertEqual(data['total_amount'], 4000000.0)
        self.assertEqual(data['total_paid'], 4000000.0)
        self.assertEqual(data['remaining_balance'], 0.0)

        # Mọi khách hàng đều có billing_status = 'PAID' và individual_balance = 0
        for p in data['passengers']:
            self.assertEqual(p['billing_status'], 'PAID')
            self.assertEqual(p['individual_balance'], 0.0)
            self.assertEqual(p['status'], 'Completed')

        print("\n[PASS] Case 3: Full Group Payment - 1 lệnh chuyển toàn bộ khách sang PAID/Completed, PNR = PAID/COMPLETED, dư nợ = 0.")

    def test_case_4_partial_cancellation_and_capacity_release(self):
        """
        Case 4: Partial Cancellation & Capacity Release
        - Phòng khám có 5 ghế. Đặt 5 khách vào cùng khung giờ 14:00 - 14:30 ngày 2026-12-05.
          + Khách 1, 2, 3: dịch vụ 500,000đ/người.
          + Khách 4, 5: dịch vụ 1,000,000đ/người.
          + Tổng ban đầu: 3,500,000đ.
        - Kiểm tra capacity ban đầu:
          + 5 khách chiếm trọn 5 ghế -> available_chairs = 0, is_available = False.
        - Hủy 2 khách (Khách 4 & Khách 5):
          + Cập nhật trạng thái thành 'Cancelled'.
        - Kết quả kiểm tra:
          + 2 khách trạng thái 'Cancelled'.
          + 3 khách còn lại trạng thái 'Confirmed'.
          + Tổng tiền phải thu PNR tự động loại bỏ tiền 2 khách bị hủy (hoặc tiền khách hủy = 0),
            tổng phải thu còn lại đúng 1,500,000đ.
          + Capacity giải phóng: gọi lại capacity check -> available_chairs = 2, ghế đã được giải phóng thành công!
        """
        pnr_code = "MSGRP4"
        test_date_str = "2026-12-05"
        test_time_str = "14:00"
        t_start = datetime(2026, 12, 5, 14, 0, tzinfo=vn_tz)
        t_end = t_start + timedelta(minutes=30)

        passengers_data = [
            ("Khách C1", "0904000001", 500000),
            ("Khách C2", "0904000002", 500000),
            ("Khách C3", "0904000003", 500000),
            ("Khách C4", "0904000004", 1000000),
            ("Khách C5", "0904000005", 1000000),
        ]

        bookings = []
        for name, phone, price in passengers_data:
            cust = Customer.objects.create(name=name, phone=phone)
            b = Booking.objects.create(
                customer=cust, clinic=self.clinic,
                pnr_code=pnr_code, group_code=pnr_code,
                start_time=t_start, end_time=t_end, status='Confirmed'
            )
            BookingDetail.objects.create(booking=b, service_detail=self.svc_han_rang, actual_price=price, quantity=1)
            Billing.objects.create(booking=b, clinic=self.clinic, subtotal=price, final_total=price, status='UNPAID')
            bookings.append(b)

        # 1. Kiểm tra capacity khi cả 5 khách đang giữ ghế
        cap_url = f'/api/capacity-check/?clinic_id={self.clinic.clinic_id}&date={test_date_str}&start_time={test_time_str}&passenger_count=1'
        res_cap_full = self.client.get(cap_url)
        self.assertEqual(res_cap_full.status_code, status.HTTP_200_OK)
        self.assertFalse(res_cap_full.data['is_available'])
        self.assertEqual(res_cap_full.data['occupied_chairs'], 5)
        self.assertEqual(res_cap_full.data['available_chairs'], 0)
        self.assertIsNotNone(res_cap_full.data['warning'])

        # 2. Hủy 2 khách: Khách C4 và Khách C5 qua API cập nhật trạng thái PNR
        b4, b5 = bookings[3], bookings[4]
        res_cancel_4 = self.client.post(f'/api/pnr/{pnr_code}/passenger/{b4.booking_id}/update/', {
            "status": "Cancelled"
        }, format='json')
        self.assertEqual(res_cancel_4.status_code, status.HTTP_200_OK)
        self.assertEqual(res_cancel_4.data['new_status'], 'Cancelled')

        res_cancel_5 = self.client.post(f'/api/pnr/{pnr_code}/passenger/{b5.booking_id}/update/', {
            "status": "Cancelled"
        }, format='json')
        self.assertEqual(res_cancel_5.status_code, status.HTTP_200_OK)
        self.assertEqual(res_cancel_5.data['new_status'], 'Cancelled')

        # 3. Tra cứu PNR sau khi hủy 2 khách
        lookup_res = self.client.get(f'/api/pnr/{pnr_code}/')
        self.assertEqual(lookup_res.status_code, status.HTTP_200_OK)
        data = lookup_res.data

        # Kiểm tra tiền PNR: đã loại bỏ 2,000,000đ của 2 khách hủy -> Tổng phải thu chỉ còn 1,500,000đ
        self.assertEqual(data['total_amount'], 1500000.0)
        self.assertEqual(data['remaining_balance'], 1500000.0)

        # Kiểm tra trạng thái từng hành khách
        passengers_map = {p['customer']['name']: p for p in data['passengers']}
        self.assertEqual(passengers_map['Khách C1']['status'], 'Confirmed')
        self.assertEqual(passengers_map['Khách C2']['status'], 'Confirmed')
        self.assertEqual(passengers_map['Khách C3']['status'], 'Confirmed')
        self.assertEqual(passengers_map['Khách C4']['status'], 'Cancelled')
        self.assertEqual(passengers_map['Khách C5']['status'], 'Cancelled')

        # Khách hủy có individual_amount = 0 (tiền thu = 0)
        self.assertEqual(passengers_map['Khách C4']['individual_amount'], 0.0)
        self.assertEqual(passengers_map['Khách C5']['individual_amount'], 0.0)

        # 4. Kiểm tra Capacity được giải phóng: Ghế trống phải tăng từ 0 lên 2 ghế
        res_cap_released = self.client.get(cap_url)
        self.assertEqual(res_cap_released.status_code, status.HTTP_200_OK)
        self.assertTrue(res_cap_released.data['is_available'])
        self.assertEqual(res_cap_released.data['occupied_chairs'], 3)
        self.assertEqual(res_cap_released.data['available_chairs'], 2)
        self.assertIsNone(res_cap_released.data['warning'])

        print("\n[PASS] Case 4: Partial Cancellation & Capacity Release - Hủy 2 khách (Cancelled), 3 khách còn lại Confirmed, tổng thu giảm từ 3.5tr còn 1.5tr, giải phóng đúng 2 ghế trống!")