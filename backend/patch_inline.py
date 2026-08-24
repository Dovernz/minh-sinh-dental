import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'@admin\.register\(Booking\)\s*(class BookingDetailInline.*?fields = \([^)]*\)\n)\n*class BookingAdmin'
match = re.search(pattern, text, re.DOTALL)
if match:
    inline_code = match.group(1)
    text = text.replace(match.group(0), inline_code + '\n@admin.register(Booking)\nclass BookingAdmin')
    with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
        f.write(text)