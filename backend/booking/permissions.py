from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from rest_framework.permissions import BasePermission


def _check_perms(user, perm_list):
    if not user or not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return any(user.has_perm(p) for p in perm_list)


def has_booking_perm(user):
    perms = [
        "booking.view_booking",
        "booking.add_booking",
        "booking.change_booking",
        "booking.delete_booking",
        "operations.view_managebooking",
        "operations.view_dailyschedule",
        "operations.view_weeklyschedule",
        "operations.change_dailyschedule",
        "operations.change_weeklyschedule",
    ]
    return _check_perms(user, perms)


def has_transaction_perm(user):
    perms = [
        "booking.view_payment",
        "booking.add_payment",
        "booking.change_payment",
        "booking.view_bookingbill",
        "booking.add_bookingbill",
        "booking.view_billing",
        "booking.add_billing",
        "booking.change_billing",
    ]
    return _check_perms(user, perms)


def has_customer_service_perm(user):
    perms = [
        "booking.view_customer",
        "booking.add_customer",
        "booking.change_customer",
        "booking.delete_customer",
        "booking.view_clinic",
        "booking.add_clinic",
        "booking.change_clinic",
        "booking.view_service",
        "booking.view_servicedetail",
        "booking.add_servicedetail",
        "booking.change_servicedetail",
        "booking.view_servicecategory",
        "booking.add_servicecategory",
        "booking.change_servicecategory",
        "booking.view_timeslot",
        "booking.change_timeslot",
        "services_menu.view_catalogdiscount",
        "booking.view_catalogdiscount",
        "services_menu.view_catalogservicedetail",
    ]
    return _check_perms(user, perms)


def has_finance_inventory_perm(user):
    perms = [
        "booking.view_inventorydetail",
        "booking.add_inventorydetail",
        "booking.change_inventorydetail",
        "booking.view_inventoryusage",
        "booking.add_inventoryusage",
        "booking.view_topupinfo",
        "booking.change_topupinfo",
        "booking.view_commissionrate",
        "booking.change_commissionrate",
    ]
    return _check_perms(user, perms)


def has_commission_perm(user):
    perms = [
        "booking.view_commissionrate",
        "booking.change_commissionrate",
        "booking.view_topupinfo",
    ]
    return _check_perms(user, perms)


def has_wordpress_perm(user):
    perms = [
        "booking.manage_wordpress_posts",
        "booking.view_article",
        "booking.add_article",
        "booking.change_article",
        "booking.delete_article",
        "booking.view_marketingarticle",
        "marketing.view_marketingarticle",
        "marketing.add_marketingarticle",
        "marketing.change_marketingarticle",
    ]
    return _check_perms(user, perms)


def has_system_user_perm(user):
    perms = [
        "auth.view_user",
        "auth.add_user",
        "auth.change_user",
        "auth.delete_user",
        "auth.view_group",
        "auth.add_group",
        "auth.change_group",
        "booking.view_employee",
        "booking.add_employee",
        "booking.change_employee",
    ]
    return _check_perms(user, perms)


def has_dental_chart_perm(user):
    perms = [
        "booking.view_customer",
        "booking.change_customer",
        "booking.view_booking",
        "booking.view_dentalchart",
        "booking.add_dentalchart",
        "booking.change_dentalchart",
        "operations.view_managebooking",
    ]
    return _check_perms(user, perms)


class HasBookingPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and has_booking_perm(request.user)
        )


class HasTransactionPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and has_transaction_perm(request.user)
        )


class HasFinanceCommissionPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and has_commission_perm(request.user)
        )


class HasDentalChartPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and has_dental_chart_perm(request.user)
        )


class HasCustomerServicePermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and has_customer_service_perm(request.user)
        )


class HasFinanceInventoryPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and has_finance_inventory_perm(request.user)
        )


class HasSystemUserPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and has_system_user_perm(request.user)
        )


class HasWordpressPermission(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_staff
            and has_wordpress_perm(request.user)
        )


class StaffPermissionRequiredMixin:
    permission_check_func = None
    api_mode = False

    def dispatch(self, request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            if self.api_mode:
                return JsonResponse(
                    {"detail": "Authentication credentials were not provided."},
                    status=401,
                )
            return redirect_to_login(request.get_full_path(), login_url="/admin/login/")

        if not request.user.is_staff or (
            self.permission_check_func
            and not self.permission_check_func(request.user)
        ):
            if self.api_mode:
                return JsonResponse(
                    {"detail": "You do not have permission to perform this action."},
                    status=403,
                )
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)