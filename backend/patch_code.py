import re
with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace(
    '# Validate Price',
    '''if row.get('code') == '':
            row['code'] = None

        # Validate Price'''
)

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)