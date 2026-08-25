import io

file_path = 'backend/operations/admin.py'
with io.open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace ts_bookings query with list comprehension
old_code = "ts_bookings = list(qs.filter(appointment_time__time=ts.start_time))"
new_code = "ts_bookings = [b for b in qs if b.appointment_time and b.appointment_time.time() == ts.start_time]"
content = content.replace(old_code, new_code)

with io.open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print("Replaced ts_bookings query")
