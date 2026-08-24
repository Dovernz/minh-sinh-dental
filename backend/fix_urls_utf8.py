file_path = "core/urls.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

import re
content = re.sub(r'admin\.site\.index_title = .*', 'admin.site.index_title = "Bảng điều khiển"', content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
