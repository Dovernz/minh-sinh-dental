from datetime import timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from booking.models import (
    Billing,
    Clinic,
    Employee,
    Customer,
    ServiceCategory,
    ServiceDetail,
    Booking,
    BookingDetail,
    CommissionRate,
    Payment,
)
from booking.commission_apis import (
    calculate_commissions,
    extract_commission_items,
    get_commission_rates,
)


class BookingCommissionTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='bs_pt')
        user2 = User.objects.create_user(username='bs_ft')

        clinic = Clinic.objects.create(name='Minh Sinh 1', address='123 Kim Ma')

        self.bs_pt = Employee.objects.create(
            user=user,
            full_name='Bác sĩ Parttime',
            contract_type='Part-time',
            clinic=clinic,
            role='Bác sĩ'
        )

        self.bs_ft = Employee.objects.create(
            user=user2,
            full_name='Bác sĩ Fulltime',
            contract_type='Hợp đồng',
            clinic=clinic,
            role='Bác sĩ'
        )

        customer = Customer.objects.create(name='Nguyễn Văn Khách', phone='0912345678')
        category = ServiceCategory.objects.create(name='Nha khoa tổng quát')
        service = ServiceDetail.objects.create(category=category, name='Lấy cao răng', price=1000000)

        booking = Booking.objects.create(
            customer=customer,
            clinic=clinic,
            status='Completed',
            start_time=timezone.now(),
            end_time=timezone.now()
        )

        self.booking_detail_pt = BookingDetail.objects.create(
            booking=booking,
            service_detail=service,
            actual_price=1000000,
            quantity=1,
            consulting_doctor=self.bs_pt,
            performing_doctor=self.bs_pt
        )

        self.booking_detail_ft = BookingDetail.objects.create(
            booking=booking,
            service_detail=service,
            actual_price=1000000,
            quantity=1,
            consulting_doctor=self.bs_ft,
            performing_doctor=self.bs_ft
        )

        CommissionRate.objects.create(
            name='Quy chế 2026',
            start_date=timezone.now().date() - timedelta(days=30),
            consulting_rate_percent=10.0,
            performing_rate_percent=15.0
        )

        billing = Billing.objects.create(booking=booking, clinic=clinic, final_total=1000000)
        Payment.objects.create(billing=billing, amount=1000000)

    def test_fulltime_doctor_zero_commission(self):
        items = extract_commission_items(calc_mode='booking')
        ft_items = [
            item for item in items
            if item.get('employee_id') == self.bs_ft.pk or item.get('doctor_id') == self.bs_ft.pk
        ]
        for item in ft_items:
            self.assertEqual(item.get('consulting_commission', 0), 0)
            self.assertEqual(item.get('performing_commission', 0), 0)

    def test_parttime_doctor_commission(self):
        items = extract_commission_items(calc_mode='booking')
        pt_items = [
            item for item in items
            if item.get('doctor_id') == self.bs_pt.pk or item.get('doctor_id') == getattr(self.bs_pt, 'employee_id', self.bs_pt.pk)
        ]
        consulting_comm = sum(item['commission'] for item in pt_items if item['role'] == 'Consulting')
        performing_comm = sum(item['commission'] for item in pt_items if item['role'] == 'Performing')

        self.assertEqual(consulting_comm, 100000.0)
        self.assertEqual(performing_comm, 150000.0)

    def test_extract_commission_items_booking_mode(self):
        items = extract_commission_items(calc_mode='booking')
        self.assertIsNotNone(items)
        self.assertTrue(len(items) > 0)

    def test_extract_commission_items_payment_mode(self):
        items = extract_commission_items(calc_mode='payment')
        self.assertIsNotNone(items)
        self.assertTrue(len(items) > 0)

    def test_api_commissions_summary(self):
        response = self.client.get('/api/reports/commissions/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIsInstance(data, list)
        self.assertTrue(len(data) > 0)
        self.assertIn('total', data[0])

    def test_api_commissions_doctor_detail(self):
        bs_pt = self.bs_pt
        emp_id = getattr(bs_pt, 'employee_id', bs_pt.pk)
        response = self.client.get(f'/api/reports/commissions/{emp_id}/')
        self.assertEqual(response.status_code, 200)