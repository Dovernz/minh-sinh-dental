import os

file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove existing if they exist (to prevent duplicates)
import re
content = re.sub(r'^LOGIN_REDIRECT_URL.*$', '', content, flags=re.MULTILINE)
content = re.sub(r'^LOGOUT_REDIRECT_URL.*$', '', content, flags=re.MULTILINE)

# Append to end of file
redirect_config = """
# Điều hướng sau khi Đăng nhập/Đăng xuất
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/login/'
"""
content += redirect_config

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated settings.py with redirect URLs.")
