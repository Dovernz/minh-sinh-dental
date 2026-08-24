import re

with open('/app/booking/admin.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Imports
if 'from import_export.formats.base_formats import XLSX, CSV' not in text:
    text = text.replace('from import_export.admin import ImportExportModelAdmin',
                        'from import_export.admin import ImportExportModelAdmin\nfrom import_export.formats.base_formats import XLSX, CSV\nfrom django.urls import path\nfrom django.http import HttpResponse')

# 2. Add formats = [XLSX, CSV]
if 'formats = [XLSX, CSV]' not in text:
    text = text.replace('    resource_classes = [ServiceDetailResource]\n',
                        '    resource_classes = [ServiceDetailResource]\n    formats = [XLSX, CSV]\n')

# 3. Add get_urls and download_template
new_methods = '''
    def get_urls(self):
        urls = super().get_urls()
        from django.urls import path
        my_urls = [
            path('import-template/', self.admin_site.admin_view(self.download_template), name='import_template_servicedetail'),
        ]
        return my_urls + urls

    def download_template(self, request):
        from django.http import HttpResponse
        resource = ServiceDetailResource()
        dataset = resource.export(queryset=self.model.objects.none())
        response = HttpResponse(dataset.xlsx, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="Template_DichVu.xlsx"'
        return response

'''
if 'def download_template' not in text:
    text = text.replace('    def has_add_permission(self, request):', new_methods + '    def has_add_permission(self, request):')

with open('/app/booking/admin.py', 'w', encoding='utf-8') as f:
    f.write(text)