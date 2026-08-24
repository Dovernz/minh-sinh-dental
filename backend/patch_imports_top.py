import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('from .models import (', 'from .models import BookingDetail, Billing\nfrom .models import (')

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)