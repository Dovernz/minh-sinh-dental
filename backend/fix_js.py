import re

with open('/app/static/js/admin_custom.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Xóa bỏ đoạn mã cũ
content = re.sub(r'let checkHeader = setInterval\(\(\) => \{[\s\S]*?\}\, 100\);', '', content)

with open('/app/static/js/admin_custom.js', 'w', encoding='utf-8') as f:
    f.write(content)
