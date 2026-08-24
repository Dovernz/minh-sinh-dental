import re

def update_admin(file_path, class_name):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    out_lines = []
    in_target_class = False

    for line in lines:
        if line.startswith('class ' + class_name):
            in_target_class = True
            out_lines.append(line)
            continue
            
        if in_target_class and line.startswith('class '):
            in_target_class = False

        if in_target_class and 'search_fields' in line and '=' in line:
            out_lines.append("    search_fields = ['category__name', 'code', 'name', 'difficulty', 'price', 'warranty']\n")
            continue
            
        if in_target_class and 'def has_add_permission' in line and 'def get_search_results' not in ''.join(out_lines):
            new_method = '''
    def get_search_results(self, request, queryset, search_term):
        original_search_fields = self.search_fields
        self.search_fields = [f for f in self.search_fields if f != 'price']
        
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        
        self.search_fields = original_search_fields
        
        if search_term:
            from django.db.models import Q, CharField
            from django.db.models.functions import Cast
            
            clean_term = search_term.replace('.', '').replace(',', '')
            if clean_term.isdigit() or search_term.strip():
                qs_price = self.model.objects.annotate(
                    price_str=Cast('price', CharField())
                ).filter(price_str__icontains=clean_term)
                queryset = queryset | qs_price
                
        return queryset, use_distinct
'''
            out_lines.append(new_method + '\n')
            out_lines.append(line)
            continue
            
        out_lines.append(line)

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

update_admin('/app/booking/admin.py', 'ServiceDetailAdmin')
update_admin('/app/services_menu/admin.py', 'CatalogServiceDetailAdmin')