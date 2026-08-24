import os

file_path = "core/urls.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

replacements = {
    "(template_name='admin/password_reset_form.html')": "()",
    "(template_name='admin/password_reset_done.html')": "()",
    "(template_name='admin/password_reset_confirm.html')": "()",
    "(template_name='admin/password_reset_complete.html')": "()"
}

for old, new in replacements.items():
    content = content.replace(old, new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
print("Updated urls.py")
