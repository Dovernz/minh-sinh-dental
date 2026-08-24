file_path = "core/settings.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace('"icon": "discount"', '"icon": "local_offer"')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
