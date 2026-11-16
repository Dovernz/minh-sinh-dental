import os
import sys
import json
import urllib.request
import urllib.parse
from decimal import Decimal
from datetime import datetime, timedelta
import zoneinfo

vn_tz = zoneinfo.ZoneInfo('Asia/Ho_Chi_Minh')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from booking.models import Clinic, Customer, ServiceCategory, ServiceDetail, Booking, BookingDetail, Billing, Payment

BASE_URL = "http://127.0.0.1:8000/api"

def http_get(path):
    url = f"{BASE_URL}{path}"
    req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode('utf-8')
            return resp.status, json.loads(data)
    except urllib.error.HTTPError as e:
        data = e.read().decode('utf-8')
        return e.code, json.loads(data) if data else {}

def http_post(path, payload):
    url = f"{BASE_URL}{path}"
    data_bytes = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data_bytes, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req) as resp:
            data = resp.read().decode('utf-8')
            return resp.status, json.loads(data)
    except urllib.error.HTTPError as e:
        data = e.read().decode('utf-8')
        return e.code, json.loads(data) if data else {}

def run_all_cases():
    results = {}
    print("================================================================================")
    print("          NHA KHOA MINH SINH - LIVE E2E PNR GROUP TESTING PROTOCOL               ")
    print("================================================================================")

    # Clean / prepare clinic
    clinic, _ = Clinic.objects.get_or_create(
        name="Minh Sinh PNR Premium Clinic",
        defaults={'address': '456 Kim Ma, Ba Dinh, Ha Noi', 'total_chairs': 5}
    )
    if clinic.total_chairs != 5:
        clinic.total_chairs = 5
        clinic.save()

    cat, _ = ServiceCategory.objects.get_or_create(name="Nha Khoa Tong Quat", defaults={'estimate_time': 30})
    svc1, _ = ServiceDetail.objects.get_or_create(category=cat, name="Cao rang danh bong", defaults={'price': 300000, 'code': 'CR01'})
    svc2, _ = ServiceDetail.objects.get_or_create(category=cat, name="Tram rang sau Composite", defaults={'price': 500000, 'code': 'TR01'})
    svc3, _ = ServiceDetail.objects.get_or_create(category=cat, name="Nho rang khon tieu phau", defaults={'price': 1200000, 'code': 'NR01'})
    svc4, _ = ServiceDetail.objects.get_or_create(category=cat, name="Tay trang rang WhiteMax", defaults={'price': 2000000, 'code': 'TT01'})

    # --------------------------------------------------------------------------------
    # CASE 1: Multi-Customer Booking & PNR Lookup
    # --------------------------------------------------------------------------------
    print("\n--- [CASE 1] Multi-Customer Booking & PNR Lookup ---")
    pnr_c1 = "MSLIVE1"
    Booking.objects.filter(pnr_code=pnr_c1).delete()

    t_base1 = datetime(2026, 12, 10, 8, 30, tzinfo=vn_tz)
    c1_specs = [
        ("Nguyen Thi Lan", "0911000001", t_base1, svc1, 300000),
        ("Tran Van Minh", "0911000002", t_base1 + timedelta(minutes=30), svc2, 500000),
        ("Le Hoang Nam", "0911000003", t_base1 + timedelta(minutes=60), svc3, 1200000),
        ("Pham Thu Ha", "0911000004", t_base1 + timedelta(minutes=90), svc4, 2000000),
    ]

    for name, phone, st, svc, price in c1_specs:
        cust, _ = Customer.objects.get_or_create(phone=phone, defaults={'name': name})
        b = Booking.objects.create(
            customer=cust, clinic=clinic,
            pnr_code=pnr_c1, group_code=pnr_c1,
            start_time=st, end_time=st + timedelta(minutes=30),
            status='Confirmed'
        )
        BookingDetail.objects.create(booking=b, service_detail=svc, actual_price=price, quantity=1)
        Billing.objects.create(booking=b, clinic=clinic, subtotal=price, final_total=price, status='UNPAID')

    c1_code, c1_data = http_get(f"/pnr/{pnr_c1}/")
    assert c1_code == 200, f"Case 1 HTTP Error: {c1_code} - {c1_data}"
    assert c1_data['total_passengers'] == 4
    assert c1_data['total_amount'] == 4000000.0
    assert c1_data['total_paid'] == 0.0
    assert c1_data['remaining_balance'] == 4000000.0
    assert c1_data['payment_status'] == 'UNPAID'
    assert len(c1_data['passengers']) == 4

    p1 = c1_data['passengers'][0]
    p4 = c1_data['passengers'][3]
    assert p1['customer']['name'] == "Nguyen Thi Lan" and p1['individual_amount'] == 300000.0
    assert p4['customer']['name'] == "Pham Thu Ha" and p4['individual_amount'] == 2000000.0

    print(f"-> CASE 1 PASSED: Tra cứu PNR {pnr_c1} thành công. 4 khách, đúng giờ khám, đúng đơn giá riêng (300k, 500k, 1.2tr, 2tr), tổng phải thu = 4,000,000 VNĐ.")
    results['Case_1'] = {"status": "PASS", "pnr": pnr_c1, "total_passengers": 4, "total_amount": 4000000, "payment_status": "UNPAID"}

    # --------------------------------------------------------------------------------
    # CASE 2: Individual / Split Payment
    # --------------------------------------------------------------------------------
    print("\n--- [CASE 2] Individual / Split Payment ---")
    pnr_c2 = "MSLIVE2"
    Booking.objects.filter(pnr_code=pnr_c2).delete()

    t_base2 = datetime(2026, 12, 11, 9, 0, tzinfo=vn_tz)
    c2_specs = [
        ("Khach A (Thanh toan rieng)", "0922000001", t_base2, svc1, 300000),
        ("Khach B (Thanh toan rieng)", "0922000002", t_base2 + timedelta(minutes=30), svc2, 500000),
        ("Khach C (Chua tra)", "0922000003", t_base2 + timedelta(minutes=60), svc3, 1200000),
        ("Khach D (Chua tra)", "0922000004", t_base2 + timedelta(minutes=90), svc4, 2000000),
    ]

    c2_bookings = []
    for name, phone, st, svc, price in c2_specs:
        cust, _ = Customer.objects.get_or_create(phone=phone, defaults={'name': name})
        b = Booking.objects.create(
            customer=cust, clinic=clinic,
            pnr_code=pnr_c2, group_code=pnr_c2,
            start_time=st, end_time=st + timedelta(minutes=30),
            status='Confirmed'
        )
        BookingDetail.objects.create(booking=b, service_detail=svc, actual_price=price, quantity=1)
        Billing.objects.create(booking=b, clinic=clinic, subtotal=price, final_total=price, status='UNPAID')
        c2_bookings.append(b)

    # Thanh toán khách A: 300,000đ
    code_pay_a, res_pay_a = http_post("/pos/individual-payment/", {
        "booking_id": c2_bookings[0].booking_id,
        "amount": 300000,
        "payment_method": "QR"
    })
    assert code_pay_a == 200 and res_pay_a['billing_status'] == 'PAID'

    # Thanh toán khách B: 500,000đ
    code_pay_b, res_pay_b = http_post("/pos/individual-payment/", {
        "booking_id": c2_bookings[1].booking_id,
        "amount": 500000,
        "payment_method": "CASH"
    })
    assert code_pay_b == 200 and res_pay_b['billing_status'] == 'PAID'

    # Tra cứu lại PNR MSLIVE2
    c2_code, c2_data = http_get(f"/pnr/{pnr_c2}/")
    assert c2_code == 200
    assert c2_data['payment_status'] == 'PARTIAL'
    assert c2_data['total_paid'] == 800000.0
    assert c2_data['remaining_balance'] == 3200000.0

    p_map2 = {p['customer']['phone']: p for p in c2_data['passengers']}
    assert p_map2['0922000001']['billing_status'] == 'PAID' and p_map2['0922000001']['individual_balance'] == 0.0
    assert p_map2['0922000002']['billing_status'] == 'PAID' and p_map2['0922000002']['individual_balance'] == 0.0
    assert p_map2['0922000003']['billing_status'] == 'UNPAID' and p_map2['0922000003']['individual_balance'] == 1200000.0
    assert p_map2['0922000004']['billing_status'] == 'UNPAID' and p_map2['0922000004']['individual_balance'] == 2000000.0

    print(f"-> CASE 2 PASSED: Thanh toán lẻ khách A & B thành công. A, B = PAID, C, D = UNPAID, PNR = PARTIAL, Đã thu: 800,000 VNĐ, Còn nợ: 3,200,000 VNĐ.")
    results['Case_2'] = {"status": "PASS", "pnr": pnr_c2, "paid": 800000, "debt": 3200000, "payment_status": "PARTIAL"}

    # --------------------------------------------------------------------------------
    # CASE 3: Full Group Payment
    # --------------------------------------------------------------------------------
    print("\n--- [CASE 3] Full Group Payment ---")
    pnr_c3 = "MSLIVE3"
    Booking.objects.filter(pnr_code=pnr_c3).delete()

    t_base3 = datetime(2026, 12, 12, 10, 0, tzinfo=vn_tz)
    c3_specs = [
        ("Nhom Truong Doan", "0933000001", t_base3, svc1, 300000),
        ("Thanh Vien 2", "0933000002", t_base3 + timedelta(minutes=30), svc2, 500000),
        ("Thanh Vien 3", "0933000003", t_base3 + timedelta(minutes=60), svc3, 1200000),
        ("Thanh Vien 4", "0933000004", t_base3 + timedelta(minutes=90), svc4, 2000000),
    ]

    for name, phone, st, svc, price in c3_specs:
        cust, _ = Customer.objects.get_or_create(phone=phone, defaults={'name': name})
        b = Booking.objects.create(
            customer=cust, clinic=clinic,
            pnr_code=pnr_c3, group_code=pnr_c3,
            start_time=st, end_time=st + timedelta(minutes=30),
            status='Confirmed'
        )
        BookingDetail.objects.create(booking=b, service_detail=svc, actual_price=price, quantity=1)
        Billing.objects.create(booking=b, clinic=clinic, subtotal=price, final_total=price, status='UNPAID')

    # Thanh toán toàn bộ nhóm bằng 1 lệnh POST tới /api/pnr/<pnr>/payment/
    code_group_pay, res_group_pay = http_post(f"/pnr/{pnr_c3}/payment/", {
        "amount": 4000000,
        "payment_method": "QR",
        "notes": "Thanh toán trọn gói đoàn PNR"
    })
    assert code_group_pay == 200
    assert res_group_pay['remaining_balance'] == 0.0

    # Tra cứu lại PNR MSLIVE3
    c3_code, c3_data = http_get(f"/pnr/{pnr_c3}/")
    assert c3_code == 200
    assert c3_data['payment_status'] == 'PAID'
    assert c3_data['group_status'] == 'COMPLETED'
    assert c3_data['total_paid'] == 4000000.0
    assert c3_data['remaining_balance'] == 0.0

    for p in c3_data['passengers']:
        assert p['billing_status'] == 'PAID'
        assert p['individual_balance'] == 0.0
        assert p['status'] == 'Completed'

    print(f"-> CASE 3 PASSED: Thanh toán toàn bộ PNR {pnr_c3} thành công. Toàn bộ 4 khách PAID/Completed, PNR = PAID, Group status = COMPLETED, Dư nợ = 0 VNĐ.")
    results['Case_3'] = {"status": "PASS", "pnr": pnr_c3, "total_paid": 4000000, "debt": 0, "payment_status": "PAID", "group_status": "COMPLETED"}

    # --------------------------------------------------------------------------------
    # CASE 4: Partial Cancellation & Capacity Release
    # --------------------------------------------------------------------------------
    print("\n--- [CASE 4] Partial Cancellation & Capacity Release ---")
    pnr_c4 = "MSLIVE4"
    Booking.objects.filter(pnr_code=pnr_c4).delete()

    t_slot_date = "2026-12-15"
    t_slot_time = "14:00"
    t_start4 = datetime(2026, 12, 15, 14, 0, tzinfo=vn_tz)
    t_end4 = t_start4 + timedelta(minutes=30)

    # Đảm bảo khung giờ này chưa có booking nào khác chiếm chỗ
    Booking.objects.filter(clinic=clinic, start_time__lt=t_end4, end_time__gt=t_start4).delete()

    c4_specs = [
        ("Khach 1 (Giu cho)", "0944000001", svc2, 500000),
        ("Khach 2 (Giu cho)", "0944000002", svc2, 500000),
        ("Khach 3 (Giu cho)", "0944000003", svc2, 500000),
        ("Khach 4 (Huy)", "0944000004", svc3, 1000000),
        ("Khach 5 (Huy)", "0944000005", svc3, 1000000),
    ]

    c4_bookings = []
    for name, phone, svc, price in c4_specs:
        cust, _ = Customer.objects.get_or_create(phone=phone, defaults={'name': name})
        b = Booking.objects.create(
            customer=cust, clinic=clinic,
            pnr_code=pnr_c4, group_code=pnr_c4,
            start_time=t_start4, end_time=t_end4,
            status='Confirmed'
        )
        BookingDetail.objects.create(booking=b, service_detail=svc, actual_price=price, quantity=1)
        Billing.objects.create(booking=b, clinic=clinic, subtotal=price, final_total=price, status='UNPAID')
        c4_bookings.append(b)

    # 1. Kiểm tra Capacity ban đầu (5 khách chiếm toàn bộ 5 ghế của phòng khám)
    cap_query = f"/capacity-check/?clinic_id={clinic.clinic_id}&date={t_slot_date}&start_time={t_slot_time}&passenger_count=1"
    code_cap_1, data_cap_1 = http_get(cap_query)
    assert code_cap_1 == 200
    assert data_cap_1['occupied_chairs'] == 5
    assert data_cap_1['available_chairs'] == 0
    assert data_cap_1['is_available'] is False
    print(f"   [Step 1] Capacity ban đầu: 5/5 ghế bị chiếm (0 ghế trống, is_available=False). Cảnh báo: {data_cap_1['warning']}")

    # 2. Hủy 2 khách (Khách 4 và Khách 5)
    b_cancel_1 = c4_bookings[3]
    b_cancel_2 = c4_bookings[4]

    code_canc_1, _ = http_post(f"/pnr/{pnr_c4}/passenger/{b_cancel_1.booking_id}/update/", {"status": "Cancelled"})
    assert code_canc_1 == 200

    code_canc_2, _ = http_post(f"/pnr/{pnr_c4}/passenger/{b_cancel_2.booking_id}/update/", {"status": "Cancelled"})
    assert code_canc_2 == 200

    # 3. Tra cứu PNR sau khi hủy
    c4_code, c4_data = http_get(f"/pnr/{pnr_c4}/")
    assert c4_code == 200
    # Tiền của 2 khách hủy đã bị loại bỏ khỏi tổng tiền phải thu: 3.5tr - 2tr = 1.5tr
    assert c4_data['total_amount'] == 1500000.0
    assert c4_data['remaining_balance'] == 1500000.0

    p_map4 = {p['customer']['phone']: p for p in c4_data['passengers']}
    assert p_map4['0944000001']['status'] == 'Confirmed' and p_map4['0944000001']['individual_amount'] == 500000.0
    assert p_map4['0944000002']['status'] == 'Confirmed' and p_map4['0944000002']['individual_amount'] == 500000.0
    assert p_map4['0944000003']['status'] == 'Confirmed' and p_map4['0944000003']['individual_amount'] == 500000.0
    assert p_map4['0944000004']['status'] == 'Cancelled' and p_map4['0944000004']['individual_amount'] == 0.0
    assert p_map4['0944000005']['status'] == 'Cancelled' and p_map4['0944000005']['individual_amount'] == 0.0
    print(f"   [Step 2] PNR Financials: Đã loại bỏ tiền 2 khách hủy khỏi tổng thu. Tổng thu cập nhật: {c4_data['total_amount']:,.0f} VNĐ (3 khách Confirmed: 500k/người, 2 khách Cancelled: 0đ).")

    # 4. Kiểm tra Capacity sau khi hủy: ghế được giải phóng
    code_cap_2, data_cap_2 = http_get(cap_query)
    assert code_cap_2 == 200
    assert data_cap_2['occupied_chairs'] == 3
    assert data_cap_2['available_chairs'] == 2
    assert data_cap_2['is_available'] is True
    print(f"   [Step 3] Capacity sau khi hủy: Đã giải phóng đúng 2 ghế trống (+2 seats, available_chairs=2, is_available=True).")

    print(f"-> CASE 4 PASSED: Hủy 2 khách (Cancelled) thành công. 3 khách còn lại Confirmed. Tiền phải thu giảm từ 3.5tr xuống 1.5tr. Ghế trống tăng từ 0 lên 2 ghế.")
    results['Case_4'] = {"status": "PASS", "pnr": pnr_c4, "total_amount": 1500000, "available_chairs": 2, "cancelled_passengers": 2, "confirmed_passengers": 3}

    print("\n================================================================================")
    print("                     E2E TESTING SUMMARY: 4/4 CASES PASSED                      ")
    print("================================================================================")
    print(json.dumps(results, indent=2))
    return results

if __name__ == '__main__':
    run_all_cases()
