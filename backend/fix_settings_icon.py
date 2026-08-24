import re

file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove SITE_ICON line
content = re.sub(r'\s*"SITE_ICON":.*?,', '', content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
