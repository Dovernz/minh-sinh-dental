from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework import status
import zoneinfo
vn_tz = zoneinfo.ZoneInfo('Asia/Ho_Chi_Minh')
from django.utils import timezone
from datetime import datetime, timedelta, timezone as dt_timezone
from django.core.management import call_command
from django.contrib.auth.models import User, Group
from booking.models import (
    Clinic, Customer, ServiceCategory, ServiceDetail, 
    Booking, BookingDetail, Billing, Payment
)
from booking.pnr_utils import generate_pnr_code

class AviationPNRTestCase(TestCase):
    def test_generate_pnr_code_format(self):
        code = generate_pnr_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isalnum())
        self.assertTrue(code.isupper())
        confusing_chars = {'0', 'O', '1', 'I'}
        for char in code:
            self.assertNotIn(char, confusing_chars)

    def test_booking_auto_pnr_on_save(self):
        clinic = Clinic.objects.create(name="Minh Sinh PNR Test", total_chairs=3)
        customer = Customer.objects.create(name="PNR User", phone="0901999888")
        t0 = datetime(2026, 11, 20, 9, 0, tzinfo=vn_tz)
        booking = Booking.objects.create(clinic=clinic, customer=customer, start_time=t0, end_time=t0 + timedelta(minutes=30))
        self.assertIsNotNone(booking.pnr_code)
        self.assertEqual(len(booking.pnr_code), 6)
        self.assertEqual(booking.group_code, booking.pnr_code)

    def test_unique_pnr_generation(self):
        codes = set()
        for _ in range(50):
            codes.add(generate_pnr_code())
        self.assertEqual(len(codes), 50)

class PNRLookupAPITestCase(APITestCase):
    fixtures = ['rbac_roles.json']

    def setUp(self):
        self.reception_user = User.objects.create_user(username='pnr_reception', is_staff=True)
        self.reception_user.groups.add(Group.objects.get(name='Reception'))
        self.client.force_authenticate(user=self.reception_user)
        self.clinic = Clinic.objects.create(name="Minh Sinh Main", total_chairs=5)
        self.cust_a = Customer.objects.create(name="Customer A", phone="0901112222")
        self.cust_b = Customer.objects.create(name="Customer B", phone="0903334444")
        
        self.cat = ServiceCategory.objects.create(name="General")
        self.svc = ServiceDetail.objects.create(category=self.cat, name="Cleaning", price=500000)
        
        t0 = datetime(2026, 11, 20, 9, 0, tzinfo=vn_tz)
        
        # Booking 1: 1,000,000
        self.b1 = Booking.objects.create(
            customer=self.cust_a, clinic=self.clinic, 
            start_time=t0, end_time=t0 + timedelta(minutes=30),
            pnr_code="MS123", group_code="MSGP99", status='Confirmed'
        )
        BookingDetail.objects.create(booking=self.b1, service_detail=self.svc, actual_price=500000, quantity=2)
        self.bill1 = Billing.objects.create(
            booking=self.b1, clinic=self.clinic, subtotal=1000000, final_total=1000000, status='UNPAID'
        )
        
        # Booking 2: 500,000
        self.b2 = Booking.objects.create(
            customer=self.cust_b, clinic=self.clinic, 
            start_time=t0, end_time=t0 + timedelta(minutes=30),
            pnr_code="MS124", group_code="MSGP99", status='Confirmed'
        )
        BookingDetail.objects.create(booking=self.b2, service_detail=self.svc, actual_price=500000, quantity=1)
        self.bill2 = Billing.objects.create(
            booking=self.b2, clinic=self.clinic, subtotal=500000, final_total=500000, status='UNPAID'
        )
        
        # Total group amount: 1,500,000. Pay 500,000.
        Payment.objects.create(billing=self.bill1, amount=500000, payment_method='CASH', total_billing=1000000, amount_remain=500000)
        self.bill1.status = 'INSTALLMENT'
        self.bill1.save()

    def test_pnr_lookup_group_details(self):
        response = self.client.get('/api/pnr/MSGP99/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Verify passenger list
        passengers = data.get('passengers', [])
        self.assertEqual(len(passengers), 2)
        self.assertEqual(data.get('total_passengers'), 2)
        
        pass_a = next(p for p in passengers if p['customer']['name'] == "Customer A")
        self.assertIsNotNone(pass_a)
        
        # Verify financial summary
        self.assertEqual(data.get('total_amount'), 1500000)
        self.assertEqual(data.get('total_paid'), 500000)
        self.assertEqual(data.get('remaining_balance'), 1000000)
        self.assertEqual(data.get('payment_status'), 'PARTIAL')

class CapacityCheckAPITestCase(APITestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(name="Capacity Clinic", total_chairs=2)
        cust0 = Customer.objects.create(name="User 0", phone="0910000000")
        cust1 = Customer.objects.create(name="User 1", phone="0910000001")
        t0 = datetime(2026, 11, 20, 9, 0, tzinfo=vn_tz)
        
        Booking.objects.create(
            clinic=self.clinic, customer=cust0, 
            start_time=t0, end_time=t0 + timedelta(minutes=30), 
            status='Confirmed'
        )
        Booking.objects.create(
            clinic=self.clinic, customer=cust1, 
            start_time=t0, end_time=t0 + timedelta(minutes=30), 
            status='Confirmed'
        )

    def test_capacity_check_full(self):
        url = f'/api/capacity-check/?clinic_id={self.clinic.clinic_id}&date=2026-11-20&start_time=09:00&passenger_count=1'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_available'])
        self.assertEqual(response.data['available_chairs'], 0)
        self.assertIsNotNone(response.data['warning'])

    def test_capacity_check_available(self):
        url = f'/api/capacity-check/?clinic_id={self.clinic.clinic_id}&date=2026-11-20&start_time=14:00&passenger_count=2'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_available'])
        self.assertEqual(response.data['available_chairs'], 2)
        self.assertIsNone(response.data['warning'])

class FlexiblePaymentAPITestCase(APITestCase):
    fixtures = ['rbac_roles.json']

    def setUp(self):
        self.reception_user = User.objects.create_user(username='pnr_reception', is_staff=True)
        self.reception_user.groups.add(Group.objects.get(name='Reception'))
        self.client.force_authenticate(user=self.reception_user)
        self.clinic = Clinic.objects.create(name="Payment Clinic", total_chairs=5)
        self.cust1 = Customer.objects.create(name="Payer 1", phone="0981111111")
        self.cust2 = Customer.objects.create(name="Payer 2", phone="0982222222")
        t0 = datetime(2026, 11, 20, 10, 0, tzinfo=vn_tz)
        
        # Bill 1: 1,000,000
        self.b1 = Booking.objects.create(
            customer=self.cust1, clinic=self.clinic, start_time=t0, end_time=t0 + timedelta(minutes=30),
            group_code="MSGP99", status='Confirmed'
        )
        self.bill1 = Billing.objects.create(booking=self.b1, clinic=self.clinic, final_total=1000000, status='UNPAID')
        
        # Bill 2: 2,000,000
        self.b2 = Booking.objects.create(
            customer=self.cust2, clinic=self.clinic, start_time=t0, end_time=t0 + timedelta(minutes=30),
            group_code="MSGP99", status='Confirmed'
        )
        self.bill2 = Billing.objects.create(booking=self.b2, clinic=self.clinic, final_total=2000000, status='UNPAID')

    def test_group_payment(self):
        # Pay 2,500,000 for the group. 
        # Logic: 1,000,000 covers bill1 (PAID), remaining 1,500,000 covers part of bill2 (INSTALLMENT)
        url = '/api/pnr/MSGP99/payment/'
        payload = {"amount": 2500000, "payment_method": "CASH"}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.bill1.refresh_from_db()
        self.bill2.refresh_from_db()
        self.assertEqual(self.bill1.status, 'PAID')
        self.assertEqual(self.bill2.status, 'INSTALLMENT')

    def test_individual_payment(self):
        url = '/api/pos/individual-payment/'
        payload = {"booking_id": self.b1.booking_id, "amount": 1000000, "payment_method": "QR"}
        response = self.client.post(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.bill1.refresh_from_db()
        self.assertEqual(self.bill1.status, 'PAID')

class ExcelImportCommandTestCase(TestCase):
    def test_import_command_dry_run(self):
        # This assumes the management command 'import_excel_2026' exists
        try:
            call_command('import_excel_2026', dry_run=True, limit=2)
            success = True
        except Exception:
            success = False
        self.assertTrue(success)