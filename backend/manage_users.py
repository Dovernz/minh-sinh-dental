from django.contrib.auth.models import User

# 1. Reset Superuser
su = User.objects.filter(is_superuser=True).first()
if su:
    su.set_password('Admin@123456')
    su.save()
    print(f"Superuser: {su.username} | Password: Admin@123456")
else:
    su = User.objects.create_superuser('admin', 'admin@example.com', 'Admin@123456')
    print(f"Superuser created: admin | Password: Admin@123456")

# 2. Create Staff user
staff, created = User.objects.get_or_create(username='letan1')
staff.set_password('Letan@123456')
staff.is_staff = True
staff.is_superuser = False
staff.save()
print(f"Staff user: {staff.username} | Password: Letan@123456")
