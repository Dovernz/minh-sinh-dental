import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Update BookingDetailInline
text = text.replace("    fields = ('service', 'price', 'quantity')", "    fields = ('service_detail', 'actual_price')")
# Wait, my previous code for BookingDetailInline was fields = ('service', 'price', 'quantity'). Let's just overwrite it entirely.

inline_old = '''class BookingDetailInline(admin.TabularInline):
    model = BookingDetail
    extra = 1
    fields = ('service', 'price', 'quantity')'''
inline_new = '''class BookingDetailInline(admin.TabularInline):
    model = BookingDetail
    extra = 1
    fields = ('service_detail', 'actual_price')'''
text = text.replace(inline_old, inline_new)

# Add readonly_fields to BookingAdmin
if 'readonly_fields' not in text.split('class BookingAdmin(BaseRBACAdmin):')[1].split('def save_model')[0]:
    # We will inject it after date_hierarchy
    text = text.replace("    date_hierarchy = 'booking_date'", "    date_hierarchy = 'booking_date'\n    readonly_fields = ('customer', 'clinic', 'category', 'booking_date', 'start_time', 'end_time', 'employee', 'doctor')")

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)