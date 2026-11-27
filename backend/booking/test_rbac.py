import datetime
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from rest_framework import status
from rest_framework.test import APITestCase

from booking.models import (
    Clinic,
    Customer,
    ServiceCategory,
    ServiceDetail,
    Booking,
    BookingDetail,
    Billing,
    Payment,
    InventoryDetail,
)

User = get_user_model()


class RBACTestCase(APITestCase):
    fixtures = ['rbac_roles.json']

    @classmethod
    def setUpTestData(cls):
        # Create users
        cls.doctor_user = User.objects.create_user(
            username='doctor_user',
            is_staff=True
        )
        cls.reception_user = User.objects.create_user(
            username='reception_user',
            is_staff=True
        )
        cls.accountant_user = User.objects.create_user(
            username='accountant_user',
            is_staff=True
        )
        cls.marketing_user = User.objects.create_user(
            username='marketing_user',
            is_staff=True
        )
        cls.non_staff_user = User.objects.create_user(
            username='non_staff_user',
            is_staff=False
        )
        cls.superuser = User.objects.create_superuser(
            username='admin_user',
            password=None,
            email='admin@example.com'
        )

        # Assign groups from fixture
        for group_name, user in [
            ('Doctor', cls.doctor_user),
            ('Reception', cls.reception_user),
            ('Accountant', cls.accountant_user),
            ('Marketing', cls.marketing_user),
        ]:
            group, created = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)

        # Create sample entities
        cls.clinic = Clinic.objects.create(
            name='Main Clinic',
            address='123 Health St',
            total_chairs=5
        )
        cls.customer = Customer.objects.create(
            name='John Doe',
            phone='0123456789'
        )
        cls.category = ServiceCategory.objects.create(name='General Care')
        cls.service = ServiceDetail.objects.create(
            category=cls.category,
            name='Consultation',
            price=150000
        )
        cls.booking = Booking.objects.create(
            clinic=cls.clinic,
            customer=cls.customer,
            category=cls.category,
            pnr_code='RBAC01',
            group_code='RBAC01',
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(minutes=30),
            status='Confirmed'
        )
        cls.booking_detail = BookingDetail.objects.create(
            booking=cls.booking,
            service_detail=cls.service,
            actual_price=150000,
            quantity=1
        )
        cls.billing = Billing.objects.create(
            booking=cls.booking,
            clinic=cls.clinic,
            subtotal=150000,
            final_total=150000,
            status='INSTALLMENT'
        )
        cls.payment = Payment.objects.create(
            billing=cls.billing,
            amount=50000,
            total_billing=150000,
            amount_remain=100000
        )
        cls.inventory_detail = InventoryDetail.objects.create(
            item_name='Dental Mirror',
            unit='Cái',
            category='Dụng cụ',
            price_per_unit=50000
        )

    def test_unauthenticated_access(self):
        """Unauthenticated requests return 401 on StaffPermissionRequiredMixin endpoints and 403 on DRF endpoints."""
        staff_mixin_endpoints = [
            '/api/reports/commissions/',
            '/api/pos/debts/',
            '/api/pos/bookings/',
            '/api/pos/master-data/',
            '/api/employees/',
            '/api/commission-stats/',
            '/api/service-stats/',
        ]
        for url in staff_mixin_endpoints:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"Expected 401 on unauthenticated GET {url}, got {response.status_code}"
            )

        drf_endpoints = [
            '/api/pnr/RBAC01/',
            '/api/pnr/RBAC01/payment/',
            '/api/pos/individual-payment/',
            '/api/dental-charts/',
            '/api/admin-timeslots/',
        ]
        for url in drf_endpoints:
            response = self.client.get(url)
            self.assertIn(
                response.status_code,
                [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
                f"Expected 401/403 on unauthenticated GET {url}, got {response.status_code}"
            )

    def test_non_staff_authenticated_access(self):
        """Non-staff authenticated user gets 403 on protected endpoints."""
        self.client.force_login(self.non_staff_user)
        protected_endpoints = [
            '/api/reports/commissions/',
            '/api/pos/debts/',
            '/api/pos/bookings/',
            '/api/pos/master-data/',
            '/api/employees/',
            '/api/commission-stats/',
            '/api/service-stats/',
            '/api/pnr/RBAC01/',
            '/api/pnr/RBAC01/payment/',
            '/api/pos/individual-payment/',
            '/api/dental-charts/',
            '/api/admin-timeslots/',
        ]
        for url in protected_endpoints:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Expected 403 for non-staff on GET {url}, got {response.status_code}"
            )

    def test_doctor_permissions(self):
        """Doctor permissions test."""
        self.client.force_login(self.doctor_user)

        # GET /api/dental-charts/
        res_get_chart = self.client.get('/api/dental-charts/')
        self.assertIn(res_get_chart.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])

        # POST /api/dental-charts/
        res_post_chart = self.client.post(
            '/api/dental-charts/',
            {
                'customer': self.customer.pk,
                'tooth_data': {'teeth': {}},
                'notes_data': {}
            },
            format='json'
        )
        self.assertEqual(res_post_chart.status_code, status.HTTP_201_CREATED)

        # GET /dental-chart/?customerId={self.customer.pk} sets csrftoken cookie
        res_dc = self.client.get(f'/dental-chart/?customerId={self.customer.pk}')
        self.assertEqual(res_dc.status_code, status.HTTP_200_OK)
        self.assertIn('csrftoken', res_dc.cookies)

        # 200 URLs
        allowed_urls = [
            f'/dental-chart/?customerId={self.customer.pk}',
            '/admin/operations/dailyschedule/',
            f'/admin/booking/customer/{self.customer.pk}/profile/',
        ]
        for url in allowed_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Doctor should have access to {url}, got {response.status_code}"
            )

        # 403 URLs
        forbidden_urls = [
            '/api/pos/debts/',
            '/api/reports/commissions/',
            '/api/employees/',
            '/admin/sso-to-wordpress/',
            '/admin/booking/commissionrate/',
        ]
        for url in forbidden_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Doctor should be forbidden from {url}, got {response.status_code}"
            )

    def test_reception_permissions(self):
        """Reception permissions test."""
        self.client.force_login(self.reception_user)

        allowed_urls = [
            '/api/pnr/RBAC01/',
            '/api/pos/debts/',
            '/api/pos/bookings/',
            '/api/admin-timeslots/',
            '/admin/pnr-lookup/',
            '/admin/booking/customer/',
            '/admin/operations/managebooking/',
        ]
        for url in allowed_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Reception should have access to {url}, got {response.status_code}"
            )

        forbidden_urls = [
            '/api/employees/',
            '/api/reports/commissions/',
            '/admin/sso-to-wordpress/',
            '/admin/booking/employee/',
        ]
        for url in forbidden_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Reception should be forbidden from {url}, got {response.status_code}"
            )

    def test_accountant_permissions(self):
        """Accountant permissions test."""
        self.client.force_login(self.accountant_user)

        allowed_urls = [
            '/api/reports/commissions/',
            '/api/commission-stats/',
            '/api/service-stats/',
            '/api/pos/debts/',
            '/admin/commissions-embed/',
            '/admin/booking/commissionrate/',
        ]
        for url in allowed_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Accountant should have access to {url}, got {response.status_code}"
            )

        forbidden_urls = [
            '/api/employees/',
            '/admin/sso-to-wordpress/',
        ]
        for url in forbidden_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Accountant should be forbidden from {url}, got {response.status_code}"
            )

    def test_marketing_permissions(self):
        """Marketing permissions test."""
        self.client.force_login(self.marketing_user)

        # 302 redirect on /admin/sso-to-wordpress/
        res_sso = self.client.get('/admin/sso-to-wordpress/')
        self.assertEqual(
            res_sso.status_code,
            status.HTTP_302_FOUND,
            f"Marketing should get 302 on /admin/sso-to-wordpress/, got {res_sso.status_code}"
        )

        forbidden_urls = [
            '/api/pnr/RBAC01/',
            '/api/pos/debts/',
            '/api/reports/commissions/',
            '/api/employees/',
            '/api/dental-charts/',
        ]
        for url in forbidden_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_403_FORBIDDEN,
                f"Marketing should be forbidden from {url}, got {response.status_code}"
            )

    def test_dynamic_permission_grant_revoke(self):
        """Dynamic permission grant/revoke of booking.manage_wordpress_posts switches doctor access."""
        self.client.force_login(self.doctor_user)
        target_url = '/admin/sso-to-wordpress/'

        # Initially 403
        res1 = self.client.get(target_url)
        self.assertEqual(res1.status_code, status.HTTP_403_FORBIDDEN)

        # Grant permission
        content_type = ContentType.objects.get_for_model(Booking)
        perm, _ = Permission.objects.get_or_create(
            codename='manage_wordpress_posts',
            content_type=content_type,
            defaults={'name': 'Can manage wordpress posts'}
        )
        self.doctor_user.user_permissions.add(perm)
        self.doctor_user = User.objects.get(pk=self.doctor_user.pk)  # Refresh user

        # Now 302 redirect
        res2 = self.client.get(target_url)
        self.assertEqual(res2.status_code, status.HTTP_302_FOUND)

        # Revoke permission
        self.doctor_user.user_permissions.remove(perm)
        self.doctor_user = User.objects.get(pk=self.doctor_user.pk)  # Refresh user

        # Returns to 403
        res3 = self.client.get(target_url)
        self.assertEqual(res3.status_code, status.HTTP_403_FORBIDDEN)

    def test_public_allow_any_endpoints(self):
        """Public AllowAny endpoints return 200 without authentication."""
        public_urls = [
            '/api/clinics/',
            '/api/services/',
            f'/api/capacity-check/?clinic_id={self.clinic.pk}&date=2026-12-01&start_time=09:00',
            '/api/settings/',
            '/api/menus/',
        ]
        for url in public_urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"Public endpoint {url} failed with status {response.status_code}"
            )

    def test_inventory_detail_orm_and_migration(self):
        """InventoryDetail ORM create/query and migration consistency check work without error."""
        call_command('makemigrations', check=True, dry_run=True)
        self.assertTrue(InventoryDetail.objects.filter(pk=self.inventory_detail.pk).exists())