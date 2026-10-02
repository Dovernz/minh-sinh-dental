import re

with open('/app/templates/admin/customer_360.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_iframe = '''    <!-- Tab 2: Dịch vụ (Next.js Embed) -->
    <div id="tab-consult" class="tab-content hidden w-full h-[800px] bg-gray-50 rounded-xl overflow-hidden border border-gray-200">
        <iframe src="http://localhost:3000/dental-chart?customerId={{ customer.pk }}" class="w-full h-full border-none"></iframe>
    </div>'''

# Replace from <div id="tab-consult" class="tab-content hidden"> to just before <!-- Tab 3: ... -->
# Using regex to match the entire tab-consult block
pattern = r'(?s)<!-- Tab 2:.*?<div id="tab-consult" class="tab-content hidden">.*?<!-- Tab 3:'
replacement = new_iframe + '\n\n    <!-- Tab 3:'

new_content = re.sub(pattern, replacement, content)

# Fallback if pattern didn't match perfectly
if new_content == content:
    pattern2 = r'(?s)<div id="tab-consult" class="tab-content hidden">.*?<!-- Tab 3:'
    replacement2 = '<div id="tab-consult" class="tab-content hidden w-full h-[800px] bg-gray-50 rounded-xl overflow-hidden border border-gray-200">\n        <iframe src="http://localhost:3000/dental-chart?customerId={{ customer.pk }}" class="w-full h-full border-none"></iframe>\n    </div>\n\n    <!-- Tab 3:'
    new_content = re.sub(pattern2, replacement2, content)

with open('/app/templates/admin/customer_360.html', 'w', encoding='utf-8') as f:
    f.write(new_content)
