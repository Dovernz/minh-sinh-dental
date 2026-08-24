import re
with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace ImportExportModelAdmin with ImportExportActionModelAdmin in imports
if 'ImportExportActionModelAdmin' not in text:
    text = text.replace('from import_export.admin import ImportExportModelAdmin',
                        'from import_export.admin import ImportExportModelAdmin, ImportExportActionModelAdmin')

# Replace inheritance for ServiceCategoryAdmin
text = re.sub(
    r'class ServiceCategoryAdmin\(ImportExportModelAdmin,\s*BaseRBACAdmin\):',
    'class ServiceCategoryAdmin(ImportExportActionModelAdmin, BaseRBACAdmin):',
    text
)

# Replace inheritance for ServiceDetailAdmin
text = re.sub(
    r'class ServiceDetailAdmin\(ImportExportModelAdmin,\s*BaseRBACAdmin\):',
    'class ServiceDetailAdmin(ImportExportActionModelAdmin, BaseRBACAdmin):',
    text
)

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)