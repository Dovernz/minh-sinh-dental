import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

old_logic = '''        code_val = row.get('code')
        # Nếu mã rỗng, None, hoặc chỉ chứa khoảng trắng thì ép về chuẩn None cho database
        if code_val in ['', None] or str(code_val).strip() == '':
            row['code'] = None'''

new_logic = '''        code_val = row.get('code')
        if not code_val or str(code_val).strip() == '' or str(code_val).lower() == 'nan':
            row['code'] = None'''

text = text.replace(old_logic, new_logic)

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)