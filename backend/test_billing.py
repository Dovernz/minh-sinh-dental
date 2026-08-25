import io
import re

file_path = 'booking/admin.py'
with io.open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace manual_total with final_total in BillingAdmin
# I'll just replace 'manual_total' with 'final_total' generally in the file 
# since there's no manual_total in models anymore.
content = content.replace('manual_total', 'final_total')

# But wait, final_total might be duplicated if it was already there!
# Let's check if final_total is already there. If it is, replacing manual_total with final_total 
# might result in ('final_total', 'final_total').
