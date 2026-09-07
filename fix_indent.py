import os
models_path = 'backend/booking/models.py'
with open(models_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "payment_method = models.CharField(max_length=20, choices=[('CASH'" in line:
        if not line.startswith("    payment_method"):
            lines[i] = "    " + line.lstrip()

with open(models_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
