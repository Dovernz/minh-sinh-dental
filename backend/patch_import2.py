import re
with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'def before_import_row' in line:
        # replace next 2 lines
        lines[i+1] = "        import pandas as pd\n"
        lines[i+2] = "        code_val = row.get('code')\n"
        lines.insert(i+3, "        if code_val == '' or pd.isna(code_val):\n")
        lines.insert(i+4, "            row['code'] = None\n")
        break

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)