from django.apps import apps
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType


class Command(BaseCommand):
    help = "Sets up 5 RBAC groups cleanly: Admin, Doctor, Reception, Accountant, Marketing."

    def grant_perms(self, group, app_label, model_name, actions):
        model_lower = model_name.lower()
        try:
            apps.get_model(app_label, model_lower)
        except LookupError:
            self.stdout.write(
                self.style.WARNING(f"Model not found: {app_label}.{model_lower}")
            )
            return

        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_lower)
        except ContentType.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f"ContentType not found: {app_label}.{model_lower}")
            )
            return

        for act in actions:
            codename = f"{act}_{model_lower}"
            try:
                perm = Permission.objects.get(content_type=ct, codename=codename)
                group.permissions.add(perm)
            except Permission.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"Permission not found: {codename} for {app_label}.{model_lower}"
                    )
                )

    def grant_codename(self, group, app_label, model_name, codename):
        model_lower = model_name.lower()
        try:
            apps.get_model(app_label, model_lower)
        except LookupError:
            self.stdout.write(
                self.style.WARNING(f"Model not found: {app_label}.{model_lower}")
            )
            return

        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_lower)
        except ContentType.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(f"ContentType not found: {app_label}.{model_lower}")
            )
            return

        try:
            perm = Permission.objects.get(content_type=ct, codename=codename)
            group.permissions.add(perm)
        except Permission.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"Permission not found: {codename} for {app_label}.{model_lower}"
                )
            )

    def handle(self, *args, **options):
        crud = ["add", "change", "delete", "view"]

        role_names = ["Admin", "Doctor", "Reception", "Accountant", "Marketing"]
        groups = {}

        for role_name in role_names:
            group, _ = Group.objects.get_or_create(name=role_name)
            group.permissions.clear()
            groups[role_name] = group

        # 1. Marketing
        m_grp = groups["Marketing"]
        self.grant_perms(m_grp, "marketing", "marketingarticle", crud)
        self.grant_perms(m_grp, "booking", "article", crud)
        self.grant_codename(m_grp, "booking", "article", "manage_wordpress_posts")
        self.grant_perms(m_grp, "booking", "menulink", crud)

        # 2. Doctor
        d_grp = groups["Doctor"]
        self.grant_perms(d_grp, "operations", "dailyschedule", ["view"])
        self.grant_perms(d_grp, "operations", "weeklyschedule", ["view"])
        self.grant_perms(d_grp, "booking", "booking", ["view"])
        self.grant_perms(d_grp, "booking", "customer", ["view", "change"])
        self.grant_perms(d_grp, "booking", "dentalchart", ["view", "add", "change"])
        self.grant_perms(d_grp, "booking", "consultation", crud)
        self.grant_perms(d_grp, "booking", "consultationdetail", crud)
        self.grant_perms(d_grp, "booking", "servicecategory", ["view"])
        self.grant_perms(d_grp, "booking", "servicedetail", ["view"])

        # 3. Reception
        r_grp = groups["Reception"]
        self.grant_perms(r_grp, "booking", "booking", crud)
        self.grant_perms(r_grp, "booking", "bookingdetail", crud)
        self.grant_perms(r_grp, "booking", "bookingstatushistory", ["view", "add"])
        self.grant_perms(r_grp, "booking", "customer", crud)
        self.grant_perms(r_grp, "booking", "clinic", ["view"])
        self.grant_perms(r_grp, "booking", "servicecategory", ["view"])
        self.grant_perms(r_grp, "booking", "servicedetail", ["view"])
        self.grant_perms(r_grp, "booking", "timeslot", ["view"])
        self.grant_perms(r_grp, "booking", "discount", ["view"])
        self.grant_perms(r_grp, "booking", "payment", ["view", "add", "change"])
        self.grant_perms(r_grp, "booking", "billing", ["view", "add", "change"])
        self.grant_perms(r_grp, "booking", "dentalchart", ["view"])
        self.grant_perms(r_grp, "services_menu", "catalogdiscount", ["view"])
        self.grant_perms(r_grp, "services_menu", "catalogservicedetail", ["view"])
        self.grant_perms(r_grp, "operations", "managebooking", crud)
        self.grant_perms(r_grp, "operations", "dailyschedule", ["view", "change"])
        self.grant_perms(r_grp, "operations", "weeklyschedule", ["view", "change"])

        # 4. Accountant
        a_grp = groups["Accountant"]
        self.grant_perms(a_grp, "booking", "payment", crud)
        self.grant_perms(a_grp, "booking", "billing", crud)
        self.grant_perms(a_grp, "booking", "commissionrate", crud)
        self.grant_perms(a_grp, "booking", "topupinfo", crud)
        self.grant_perms(a_grp, "booking", "inventorydetail", crud)
        self.grant_perms(a_grp, "booking", "inventoryusage", crud)
        self.grant_perms(a_grp, "booking", "booking", ["view"])
        self.grant_perms(a_grp, "booking", "bookingdetail", ["view"])
        self.grant_perms(a_grp, "booking", "customer", ["view"])
        self.grant_perms(a_grp, "booking", "clinic", ["view"])
        self.grant_perms(a_grp, "booking", "servicecategory", ["view"])
        self.grant_perms(a_grp, "booking", "servicedetail", ["view"])
        self.grant_perms(a_grp, "services_menu", "catalogdiscount", crud)
        self.grant_perms(a_grp, "services_menu", "catalogservicedetail", crud)

        # 5. Admin
        adm_grp = groups["Admin"]
        admin_models = [
            ("auth", "user"),
            ("auth", "group"),
            ("booking", "employee"),
            ("booking", "booking"),
            ("booking", "bookingdetail"),
            ("booking", "bookingstatushistory"),
            ("booking", "customer"),
            ("booking", "clinic"),
            ("booking", "servicecategory"),
            ("booking", "servicedetail"),
            ("booking", "timeslot"),
            ("booking", "dentalchart"),
            ("booking", "payment"),
            ("booking", "billing"),
            ("booking", "commissionrate"),
            ("booking", "topupinfo"),
            ("booking", "inventorydetail"),
            ("booking", "inventoryusage"),
            ("booking", "discount"),
            ("booking", "consultation"),
            ("booking", "consultationdetail"),
            ("booking", "article"),
            ("booking", "menulink"),
            ("marketing", "marketingarticle"),
            ("operations", "managebooking"),
            ("operations", "dailyschedule"),
            ("operations", "weeklyschedule"),
            ("services_menu", "catalogdiscount"),
            ("services_menu", "catalogservicedetail"),
        ]
        for app_label, model_name in admin_models:
            self.grant_perms(adm_grp, app_label, model_name, crud)
        self.grant_codename(adm_grp, "booking", "article", "manage_wordpress_posts")

        self.stdout.write(
            self.style.SUCCESS("Successfully configured RBAC roles and permissions.")
        )