import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
try:
    django.setup()
except Exception:
    os.environ['DJANGO_SETTINGS_MODULE'] = 'dental_backend.settings'
    django.setup()

from rest_framework.test import APIRequestFactory
from booking.models import Clinic, ServiceCategory, Booking, Customer
from booking.views import BookingCreateView, BookingGroupDetailView

def test_multi_customer_booking():
    print("=== BAT DAU KIEM THU BOOKING MULTI-CUSTOMER VA GROUP CODE ===")
    factory = APIRequestFactory()

    # 1. Chuan bi Clinic va ServiceCategory
    clinic, _ = Clinic.objects.get_or_create(
        name="Nha Khoa Minh Sinh - Co So Test",
        defaults={'address': '123 Nguyen Trai, Ha Noi', 'total_chairs': 5}
    )
    if clinic.total_chairs < 2:
        clinic.total_chairs = 5
        clinic.save()

    cat1, _ = ServiceCategory.objects.get_or_create(name="Nho rang khon test", defaults={'estimate_time': 30})
    cat2, _ = ServiceCategory.objects.get_or_create(name="Tay trang rang test", defaults={'estimate_time': 45})

    payload = {
        "clinic_id": clinic.clinic_id,
        "date": "2026-12-01",
        "start_time": "09:00",
        "patients": [
            {
                "fullName": "Nguyen Van Test 1",
                "phone": "0901000001",
                "email": "test1@minhsinh.vn",
                "start_time": "09:00",
                "category_id": cat1.category_id,
            },
            {
                "fullName": "Tran Thi Test 2",
                "phone": "0901000002",
                "email": "test2@minhsinh.vn",
                "start_time": "10:00",
                "category_id": cat2.category_id,
            }
        ]
    }

    # 2. Goi API BookingCreateView
    view = BookingCreateView.as_view()
    request = factory.post('/bookings/', data=payload, format='json')
    response = view(request)

    assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.content}"
    res_data = json.loads(response.content.decode('utf-8'))
    print(f"[OK] Response 201: {res_data}")

    group_code = res_data.get('group_code')
    created_ids = res_data.get('created_booking_ids')

    assert group_code and group_code.startswith("MS-GRP-"), f"Invalid group_code: {group_code}"
    assert len(created_ids) == 2, f"Expected 2 created_booking_ids, got {created_ids}"
    assert res_data.get('booking_id') == created_ids[0], "booking_id mismatch"
    print(f"[OK] Group code sinh dung format: {group_code}")

    # 3. Kiem tra DB tao dung 2 records Booking
    b1 = Booking.objects.get(pk=created_ids[0])
    b2 = Booking.objects.get(pk=created_ids[1])

    assert b1.group_code == group_code, f"Booking 1 group_code mismatch: {b1.group_code}"
    assert b2.group_code == group_code, f"Booking 2 group_code mismatch: {b2.group_code}"
    assert b1.customer.name == "Nguyen Van Test 1"
    assert b2.customer.name == "Tran Thi Test 2"
    assert b1.category_id == cat1.category_id
    assert b2.category_id == cat2.category_id
    print("[OK] DB records kiem tra chinh xac: 2 bookings chung group_code, rieng category & time.")

    # 4. Kiem tra tinh trang nhom doc lap va hoan thanh
    # Ban dau ca 2 Pending -> IN_PROGRESS
    assert b1.get_group_status() == 'IN_PROGRESS', f"Expected IN_PROGRESS, got {b1.get_group_status()}"
    print(f"[OK] Group status ban dau: {b1.get_group_status()}")

    # Cập nhat b1 Completed, b2 van Pending -> IN_PROGRESS
    b1.status = 'Completed'
    b1.save()
    b1.refresh_from_db()
    assert b1.get_group_status() == 'IN_PROGRESS', f"Expected IN_PROGRESS, got {b1.get_group_status()}"
    print("[OK] 1 khach Completed, 1 khach Pending -> Group status: IN_PROGRESS")

    # Cập nhat b2 Completed -> COMPLETED
    b2.status = 'Completed'
    b2.save()
    b1.refresh_from_db()
    assert b1.get_group_status() == 'COMPLETED', f"Expected COMPLETED, got {b1.get_group_status()}"
    print(f"[OK] Ca 2 khach Completed -> Group status: {b1.get_group_status()}")

    # 5. Kiem tra API BookingGroupDetailView
    group_view = BookingGroupDetailView.as_view()
    group_req = factory.get(f'/bookings/group/{group_code}/')
    group_res = group_view(group_req, group_code=group_code)
    assert group_res.status_code == 200, f"Group detail view failed: {group_res.status_code}"
    group_data = group_res.data
    assert group_data.get('group_code') == group_code
    assert group_data.get('group_status') == 'COMPLETED'
    assert len(group_data.get('bookings', [])) == 2
    print(f"[OK] BookingGroupDetailView tra cuu thanh cong cho nhom {group_code}")

    print("\n>>> ALL_TESTS_PASSED: BACKEND MULTI-CUSTOMER BOOKING HOAT DONG HOAN HAO! <<<")

if __name__ == '__main__':
    test_multi_customer_booking()
