import re
with open('/app/templates/admin/customer_360.html', 'r', encoding='utf-8') as f:
    html = f.read()

tabs = re.findall(r'<div[^>]*id="tab-[^>]*>.*?(?=</div><!-- /tab-)', html, re.DOTALL)
if not tabs:
    tabs = re.findall(r'<div[^>]*class="[^"]*tab-pane[^"]*"[^>]*>.*?(?=</div>\s*<div[^>]*class="[^"]*tab-pane)', html + '<div class="tab-pane', re.DOTALL)

for t in tabs:
    print("TAB FOUND:", t[:100].strip().replace('\n', ' '))
