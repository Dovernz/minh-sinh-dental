import re
with open('booking/admin.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = []
skip = False
for line in lines:
    if line.startswith('class ServiceCategoryResource'):
        skip = True
    if line.startswith('class ServiceDetailResource'):
        skip = True
    if line.startswith('@admin.register(ServiceCategory)'):
        skip = True
    if line.startswith('@admin.register(ServiceDetail)'):
        skip = True
        
    if skip:
        # Stop skipping if we hit the next class or @admin
        if line.startswith('@admin.register(TimeSlot)'):
            skip = False
            out.append(line)
        continue
    
    out.append(line)

with open('booking/admin.py', 'w', encoding='utf-8') as f:
    f.writelines(out)
