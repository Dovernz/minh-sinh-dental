import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Fix list_display
text = text.replace("list_display = ('booking_id', 'customer', 'doctor', 'category', 'service_detail', 'actual_price', 'booking_date', 'start_time')", 
                    "list_display = ('booking_id', 'customer', 'category', 'booking_date', 'start_time')")
# Fix list_filter
text = text.replace("list_filter = ('booking_date', 'clinic', 'category', 'doctor')", 
                    "list_filter = ('booking_date', 'clinic', 'category')")
# Fix readonly_fields
text = text.replace("readonly_fields = ('customer', 'clinic', 'category', 'booking_date', 'start_time', 'end_time', 'employee', 'doctor')",
                    "readonly_fields = ('customer', 'clinic', 'category', 'booking_date', 'start_time', 'end_time', 'employee')")

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)

with open('/app/operations/admin.py', 'r', encoding='utf-8') as f:
    text2 = f.read()

text2 = text2.replace("list_display = ('booking_id', 'customer', 'doctor', 'category', 'service_detail', 'current_status', 'total_paid', 'quick_payment_ui')",
                      "list_display = ('booking_id', 'customer', 'category', 'current_status', 'total_paid', 'quick_payment_ui')")
text2 = text2.replace("list_editable = ('doctor', 'service_detail')", "list_editable = ()")
text2 = text2.replace("list_filter = ('booking_date', 'clinic', 'category', 'doctor')", "list_filter = ('booking_date', 'clinic', 'category')")

with open('/app/operations/admin.py', 'w', encoding='utf-8') as f:
    f.write(text2)