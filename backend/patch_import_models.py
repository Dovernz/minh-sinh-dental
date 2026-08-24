import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from booking.models import Booking, Clinic, ServiceCategory, ServiceDetail, Employee, Customer, Payment, TopupInfo',
                    'from booking.models import Booking, Clinic, ServiceCategory, ServiceDetail, Employee, Customer, Payment, TopupInfo, BookingDetail')

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)