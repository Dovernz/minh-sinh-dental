import json
from datetime import datetime, time, timedelta
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework.test import APIClient

from booking.models import Clinic, TimeSlot, ServiceCategory, Booking, Customer


class CapacitySyncTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.web_client = Client()

        # Create Clinic
        self.clinic = Clinic.objects.create(
            name='Phòng khám Test',
            address='123 Đường Test',
            hotline='0900000001',
            total_chairs=5
        )

        # Create TimeSlots
        self.slot_1 = TimeSlot.objects.create(start_time=time(13, 30), end_time=time(14, 0))
        self.slot_2 = TimeSlot.objects.create(start_time=time(14, 0), end_time=time(14, 30))

        # Create ServiceCategory
        self.category = ServiceCategory.objects.create(
            name='Khám tổng quát',
            estimate_time=30
        )

        # Target Date setup
        self.target_date = timezone.localdate() + timedelta(days=2)
        self.date_str = self.target_date.strftime('%Y-%m-%d')

        # Create Superuser
        self.superuser = User.objects.create_superuser(
            username='qa_admin',
            password=None,
            email='qa_admin@example.com'
        )

    def test_capacity_check_api(self):
        url = f'/api/capacity-check/?clinic_id={self.clinic.clinic_id}&date={self.date_str}&start_time=13:30&passenger_count=7'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertEqual(data.get('total_chairs'), 5)
        self.assertEqual(data.get('active_bookings'), 0)
        self.assertEqual(data.get('available_chairs'), 5)
        self.assertIsNotNone(data.get('warning_message'))

    def test_distribute_preview_api(self):
        url = '/api/bookings/distribute-preview/'
        payload = {
            'clinic_id': self.clinic.clinic_id,
            'date': self.date_str,
            'start_time': '13:30',
            'passenger_count': 7,
            'duration': 30
        }
        response = self.client.post(url, payload, format='json')
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        
        self.assertTrue(data.get('needs_distribution'))
        
        distribution_summary = data.get('distribution_summary', {})
        # Depending on implementation structure, distribution_summary might be a list or dict. 
        # Checking standard structures or iterating over typical representations.
        # Here we look for slots '13:30' with count 5 and '14:00' with count 2.
        if isinstance(distribution_summary, dict):
            self.assertEqual(distribution_summary.get('13:30'), 5)
            self.assertEqual(distribution_summary.get('14:00'), 2)
        elif isinstance(distribution_summary, list):
            slot_counts = {item.get('start_time'): item.get('assigned_count') for item in distribution_summary}
            self.assertEqual(slot_counts.get('13:30'), 5)
            self.assertEqual(slot_counts.get('14:00'), 2)

    def test_booking_create_auto_distribute_false_and_true(self):
        patients = [
            {
                'fullName': f'Khách Test {i}',
                'phone': f'090100000{i}',
                'start_time': '13:30',
                'category_id': self.category.category_id
            }
            for i in range(1, 8)
        ]

        url = '/api/bookings/'

        # Test auto_distribute = False
        payload_false = {
            'clinic_id': self.clinic.clinic_id,
            'date': self.date_str,
            'auto_distribute': False,
            'patients': patients
        }
        response_false = self.client.post(url, payload_false, format='json')
        self.assertEqual(response_false.status_code, 400)
        self.assertIn('suggested_distribution', response_false.json())

        # Test auto_distribute = True
        payload_true = {
            'clinic_id': self.clinic.clinic_id,
            'date': self.date_str,
            'auto_distribute': True,
            'patients': patients
        }
        response_true = self.client.post(url, payload_true, format='json')
        self.assertEqual(response_true.status_code, 201)
        
        self.assertEqual(Booking.objects.filter(clinic=self.clinic).count(), 7)

        bookings = Booking.objects.filter(clinic=self.clinic).order_by('start_time')
        time_1330_count = 0
        time_1400_count = 0

        for b in bookings:
            time_str = timezone.localtime(b.start_time).strftime('%H:%M')
            if time_str == '13:30':
                time_1330_count += 1
            elif time_str == '14:00':
                time_1400_count += 1

        self.assertEqual(time_1330_count, 5)
        self.assertEqual(time_1400_count, 2)

    def test_daily_schedule_admin_shows_bookings(self):
        patients = [
            {
                'fullName': f'AdminCheckPatient_{i}',
                'phone': f'090200000{i}',
                'start_time': '13:30',
                'category_id': self.category.category_id
            }
            for i in range(1, 8)
        ]

        url = '/api/bookings/'
        payload_true = {
            'clinic_id': self.clinic.clinic_id,
            'date': self.date_str,
            'auto_distribute': True,
            'patients': patients
        }
        response_create = self.client.post(url, payload_true, format='json')
        self.assertEqual(response_create.status_code, 201)

        self.web_client.force_login(self.superuser)
        admin_url = f'/admin/operations/dailyschedule/?custom_clinic={self.clinic.clinic_id}&custom_date={self.date_str}'
        response = self.web_client.get(admin_url)

        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')

        for i in range(1, 8):
            self.assertIn(f'AdminCheckPatient_{i}', content)