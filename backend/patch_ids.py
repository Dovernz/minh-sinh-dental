import re

with open('/app/booking/models.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Add ID fields
replacements = {
    'class Clinic(models.Model):': 'class Clinic(models.Model):\n    clinic_id = models.AutoField(primary_key=True)',
    'class ServiceCategory(models.Model):': 'class ServiceCategory(models.Model):\n    category_id = models.AutoField(primary_key=True)',
    'class ServiceDetail(models.Model):': 'class ServiceDetail(models.Model):\n    service_id = models.AutoField(primary_key=True)',
    'class TimeSlot(models.Model):': 'class TimeSlot(models.Model):\n    timeslot_id = models.AutoField(primary_key=True)',
    'class Customer(models.Model):': 'class Customer(models.Model):\n    customer_id = models.AutoField(primary_key=True)',
    'class Employee(models.Model):': 'class Employee(models.Model):\n    employee_id = models.AutoField(primary_key=True)',
    'class Booking(models.Model):': 'class Booking(models.Model):\n    booking_id = models.AutoField(primary_key=True)',
    'class BookingStatus(models.Model):': 'class BookingStatus(models.Model):\n    status_id = models.AutoField(primary_key=True)',
    'class Payment(models.Model):': 'class Payment(models.Model):\n    payment_id = models.AutoField(primary_key=True)',
    'class InventoryDetail(models.Model):': 'class InventoryDetail(models.Model):\n    item_id = models.AutoField(primary_key=True)',
    'class InventoryUsage(models.Model):': 'class InventoryUsage(models.Model):\n    usage_id = models.AutoField(primary_key=True)',
    'class Article(models.Model):': 'class Article(models.Model):\n    article_id = models.AutoField(primary_key=True)',
    'class TopupInfo(models.Model):': 'class TopupInfo(models.Model):\n    topup_id = models.AutoField(primary_key=True)'
}

for k, v in replacements.items():
    text = text.replace(k, v)

# Fix created_at -> created_on in BookingStatus and Payment
text = re.sub(r'created_at = models\.DateTimeField\(auto_now_add=True\)', r'created_on = models.DateTimeField(auto_now_add=True)', text)

with open('/app/booking/models.py', 'w', encoding='utf-8') as f:
    f.write(text)