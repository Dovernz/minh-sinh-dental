import re

file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove SITE_SYMBOL completely
content = re.sub(r'\s*"SITE_SYMBOL":\s*"/static/img/logo.jpg",', '', content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated settings.py")
