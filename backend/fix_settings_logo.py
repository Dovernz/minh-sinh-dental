import re

file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove SITE_ICON and SITE_SYMBOL
content = re.sub(r'\s*"SITE_ICON":.*?,', '', content)
content = re.sub(r'\s*"SITE_SYMBOL":.*?,', '', content)

# Set SITE_LOGO exactly as requested
# First, remove existing SITE_LOGO
content = re.sub(r'\s*"SITE_LOGO":.*?,', '', content)

# Inject SITE_LOGO after SITE_HEADER
content = content.replace('"SITE_HEADER": "Nha Khoa Minh Sinh",', '"SITE_HEADER": "Nha Khoa Minh Sinh",\n    "SITE_LOGO": lambda request: "/static/img/logo.jpg",\n    "SITE_SYMBOL": "local_hospital",  # Just in case unfold crashes without symbol, but Ill remove it completely as user asked.')

# Wait, user said Xóa SITE_SYMBOL. I'll just remove it.
content = content.replace('    "SITE_SYMBOL": "local_hospital",  # Just in case unfold crashes without symbol, but Ill remove it completely as user asked.', '')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
