import re

with open('booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Remove BookingDetails import
text = text.replace(' BookingDetails, PaymentConfig', ' PaymentConfig')

# Replace list_display in BookingAdmin
old_list_display = " list_display = customer clinic service doctor booking_date start_time \
new_list_display
