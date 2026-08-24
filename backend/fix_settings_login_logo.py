import re

file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace SITE_LOGO lambda with static string
content = re.sub(r'\s*"SITE_LOGO":.*?,', '', content)
# It's possible there's no SITE_LOGO anymore if previous regex stripped it weirdly, but let's just insert it safely
content = content.replace('"SITE_HEADER": "Nha Khoa Minh Sinh",', '"SITE_HEADER": "Nha Khoa Minh Sinh",\n    "SITE_LOGO": "/static/img/logo.jpg",\n    "SITE_SYMBOL": "/static/img/logo.jpg",')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated settings.py")
