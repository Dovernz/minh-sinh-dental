import json
from datetime import datetime, time, timedelta
from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APIClient
from booking.models import Clinic, TimeSlot, ServiceCategory, Booking, Customer

class UXBookingSyncTestCase(TestCase):
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='PK Test',
            address='123',
            hotline='0900',
            total_chairs=5
        )
        
        TimeSlot.objects.create(start_time=time(8, 0), end_time=time(8, 30))
        TimeSlot.objects.create(start_time=time(8, 30), end_time=time(9, 0))
        TimeSlot.objects.create(start_time=time(9, 0), end_time=time(9, 30))
        
        self.category = ServiceCategory.objects.create(
            name='Kham',
            estimate_time=30
        )
        
        self.client = APIClient()
        self.future_date = timezone.localdate() + timedelta(days=2)
        self.date_str = self.future_date.strftime('%Y-%m-%d')

    def test_guest_order_and_notes_persistence(self):
        patients = [
            {'fullName': 'Khach 1', 'phone': '0901', 'note': 'Dau rang', 'start_time': '08:00', 'category_id': self.category.category_id},
            {'fullName': 'Khach 2', 'phone': '0902', 'note': '', 'start_time': '08:00', 'category_id': self.category.category_id},
            {'fullName': 'Khach 3', 'phone': '0903', 'note': '', 'start_time': '08:00', 'category_id': self.category.category_id}
        ]
        
        payload = {
            'clinic_id': self.clinic.clinic_id,
            'date': self.date_str,
            'patients': patients
        }
        
        response = self.client.post('/api/bookings/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        group_code = data.get('group_code')
        bookings_resp = data.get('bookings', [])
        
        # Check response labels and order
        for i, b in enumerate(bookings_resp, 1):
            self.assertEqual(b['guest_order'], i)
            self.assertEqual(b['guest_label'], f'Khách {i}')
            
        # Check DB notes and order
        db_bookings = Booking.objects.filter(clinic=self.clinic).order_by('guest_order')
        self.assertEqual(db_bookings[0].notes, '[Khách 1] Dau rang')
        self.assertEqual(db_bookings[1].notes, 'Khách 2')
        self.assertEqual(db_bookings[2].notes, 'Khách 3')
        self.assertEqual(db_bookings[0].guest_order, 1)
        
        # Check Group API
        group_res = self.client.get(f'/api/bookings/group/{group_code}/')
        self.assertEqual(group_res.status_code, 200)
        group_data = group_res.json()
        group_bookings = group_data.get('bookings', [])
        self.assertEqual(len(group_bookings), 3)
        self.assertEqual(group_bookings[0]['guest_label'], 'Khách 1')
        self.assertEqual(group_bookings[0]['guest_order'], 1)
        self.assertEqual(group_bookings[1]['guest_label'], 'Khách 2')
        self.assertEqual(group_bookings[2]['guest_label'], 'Khách 3')

    def test_auto_distribute_over_5_guests(self):
        patients = [
            {'fullName': f'Khach {i}', 'phone': f'090{i}', 'start_time': '08:00', 'category_id': self.category.category_id}
            for i in range(1, 8)
        ]
        
        # 1. Preview
        preview_payload = {
            'clinic_id': self.clinic.clinic_id,
            'date': self.date_str,
            'start_time': '08:00',
            'passenger_count': 7,
            'duration': 30
        }
        preview_res = self.client.post('/api/bookings/distribute-preview/', preview_payload, format='json')
        self.assertEqual(preview_res.status_code, 200)
        self.assertTrue(preview_res.json().get('needs_distribution'))
        
        # 2. Create with auto_distribute
        payload = {
            'clinic_id': self.clinic.clinic_id,
            'date': self.date_str,
            'auto_distribute': True,
            'patients': patients
        }
        response = self.client.post('/api/bookings/', payload, format='json')
        self.assertEqual(response.status_code, 201)
        
        data = response.json()
        self.assertTrue(data.get('auto_distributed'))
        
        # Verify distribution in DB
        bookings_0800 = Booking.objects.filter(
            clinic=self.clinic, 
            start_time__time=time(8, 0)
        ).count()
        bookings_0830 = Booking.objects.filter(
            clinic=self.clinic, 
            start_time__time=time(8, 30)
        ).count()
        
        self.assertEqual(bookings_0800, 5)
        self.assertEqual(bookings_0830, 2)
        
        # Verify guest_order 1..7
        all_bookings = Booking.objects.filter(clinic=self.clinic).order_by('guest_order')
        orders = [b.guest_order for b in all_bookings]
        self.assertEqual(orders, [1, 2, 3, 4, 5, 6, 7])

    def test_available_slots_full_and_remaining_capacity(self):
        # Create 5 bookings at 08:00
        dt_0800 = timezone.make_aware(datetime.combine(self.future_date, time(8, 0)))
        dt_0830 = timezone.make_aware(datetime.combine(self.future_date, time(8, 30)))
        dt_0900 = timezone.make_aware(datetime.combine(self.future_date, time(9, 0)))
        
        for i in range(5):
            cust = Customer.objects.create(name=f'C{i}', phone=f'p{i}')
            Booking.objects.create(
                clinic=self.clinic, customer=cust, category=self.category,
                start_time=dt_0800, end_time=dt_0830, status='Pending'
            )
            
        # Create 2 bookings at 08:30
        for i in range(5, 7):
            cust = Customer.objects.create(name=f'C{i}', phone=f'p{i}')
            Booking.objects.create(
                clinic=self.clinic, customer=cust, category=self.category,
                start_time=dt_0830, end_time=dt_0900, status='Pending'
            )
            
        url = f'/api/available-slots/?clinic_id={self.clinic.clinic_id}&date={self.date_str}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        slots = response.json()
        
        # Slot 08:00
        s1 = next(s for s in slots if s['start_time'] == '08:00')
        self.assertEqual(s1['total_chairs'], 5)
        self.assertEqual(s1['booked_count'], 5)
        self.assertEqual(s1['available_chairs'], 0)
        self.assertTrue(s1['is_full'])
        self.assertFalse(s1['is_past'])
        self.assertFalse(s1['is_available'])
        self.assertEqual(s1['status'], 'full')
        
        # Slot 08:30
        s2 = next(s for s in slots if s['start_time'] == '08:30')
        self.assertEqual(s2['booked_count'], 2)
        self.assertEqual(s2['available_chairs'], 3)
        self.assertFalse(s2['is_full'])
        self.assertTrue(s2['is_available'])
        self.assertEqual(s2['status'], 'available')
        
        # Slot 09:00
        s3 = next(s for s in slots if s['start_time'] == '09:00')
        self.assertEqual(s3['booked_count'], 0)
        self.assertEqual(s3['available_chairs'], 5)
        self.assertEqual(s3['status'], 'available')

    def test_available_slots_past_date_marked_past(self):
        yesterday = timezone.localdate() - timedelta(days=1)
        url = f'/api/available-slots/?clinic_id={self.clinic.clinic_id}&date={yesterday.strftime("%Y-%m-%d")}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        slots = response.json()
        
        for s in slots:
            self.assertTrue(s['is_past'])
            self.assertFalse(s['is_available'])
            self.assertEqual(s['status'], 'past')