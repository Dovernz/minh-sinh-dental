import re
with open('booking/admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(r'class ServiceCategoryResource.*?import_id_fields = \(\'name\',\)\n', '', content, flags=re.DOTALL)
content = re.sub(r'class ServiceDetailResource.*?, " \.join\(valid_difficulties\)\)\n',
