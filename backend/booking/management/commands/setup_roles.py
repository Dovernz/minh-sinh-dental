from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

class Command(BaseCommand):
    help = 'Setup RBAC Groups and Permissions'

    def grant_perms(self, group, app_label, model_name, actions):
        try:
            ct = ContentType.objects.get(app_label=app_label, model=model_name.lower())
            for act in actions:
                codename = f'{act}_{model_name.lower()}'
                try:
                    p = Permission.objects.get(content_type=ct, codename=codename)
                    group.permissions.add(p)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Permission {codename} not found'))
        except ContentType.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'ContentType {app_label}.{model_name} not found'))

    def handle(self, *args, **kwargs):
        # Create groups
        roles = ['Admin', 'Doctor', 'Reception', 'Marketing']
        groups = {}
        for role in roles:
            group, created = Group.objects.get_or_create(name=role)
            groups[role] = group
            # Clear old permissions to ensure exact setup
            group.permissions.clear()

        CRUD = ['add', 'change', 'delete', 'view']
        VIEW = ['view']

        # Marketing
        self.grant_perms(groups['Marketing'], 'marketing', 'marketingarticle', CRUD)
        self.grant_perms(groups['Marketing'], 'booking', 'article', CRUD)

        # Reception
        reception_models = [
            ('booking', 'booking'),
            ('booking', 'customer'),
            ('booking', 'service'),
            ('booking', 'clinic'),
            ('booking', 'timeslot'),
            ('operations', 'managebooking')
        ]
        for app, mod in reception_models:
            self.grant_perms(groups['Reception'], app, mod, CRUD)

        # Doctor
        self.grant_perms(groups['Doctor'], 'operations', 'dailyschedule', VIEW)
        self.grant_perms(groups['Doctor'], 'operations', 'weeklyschedule', VIEW)

        # Admin
        self.grant_perms(groups['Admin'], 'auth', 'user', CRUD)
        self.grant_perms(groups['Admin'], 'auth', 'group', CRUD)
        self.grant_perms(groups['Admin'], 'booking', 'employee', CRUD)

        self.stdout.write(self.style.SUCCESS('Successfully setup groups and permissions'))
