import os
import re

# 1. Fix booking/admin.py
booking_admin_path = 'backend/booking/admin.py'
with open(booking_admin_path, 'r', encoding='utf-8') as f:
    booking_admin = f.read()

booking_admin = booking_admin.replace(
    "list_display = ('booking', 'amount', 'payment_method', 'created_at')",
    "list_display = ('billing', 'amount', 'payment_method', 'created_at')"
)
booking_admin = booking_admin.replace(
    "search_fields = ('booking__customer__name',)",
    "search_fields = ('billing__booking__customer__name',)"
)

with open(booking_admin_path, 'w', encoding='utf-8') as f:
    f.write(booking_admin)


# 2. Fix operations/admin.py
operations_admin_path = 'backend/operations/admin.py'
with open(operations_admin_path, 'r', encoding='utf-8') as f:
    operations_admin = f.read()

# Remove PaymentInline from ManageBooking inlines
operations_admin = operations_admin.replace(
    "inlines = [BookingStatusHistoryInline, PaymentInline]",
    "inlines = [BookingStatusHistoryInline]"
)

with open(operations_admin_path, 'w', encoding='utf-8') as f:
    f.write(operations_admin)

print("Fixed admin issues!")
