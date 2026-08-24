with open('/app/booking/admin.py', 'rb') as f:
    raw = f.read()

raw = raw.replace(b'\xef\xbb\xbf', b'')

with open('/app/booking/admin.py', 'wb') as f:
    f.write(raw)