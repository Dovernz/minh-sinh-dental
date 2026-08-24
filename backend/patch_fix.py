import re

def fix_decorator(file_path, model_name, class_name):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    # Find the filter code block (everything from class PriceRangeFilter up to just before class class_name)
    pattern = r'@admin\.register\(' + model_name + r'\)\s*(class PriceRangeFilter.*?return queryset\n)\n*class ' + class_name
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        filter_code = match.group(1)
        # Remove the wrong block
        text = text.replace(match.group(0), filter_code + '\n@admin.register(' + model_name + ')\nclass ' + class_name)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(text)

fix_decorator('/app/booking/admin.py', 'ServiceDetail', 'ServiceDetailAdmin')
fix_decorator('/app/services_menu/admin.py', 'CatalogServiceDetail', 'CatalogServiceDetailAdmin')
