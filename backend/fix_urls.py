file_path = "core/urls.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

if "admin.site.site_header" not in content:
    content += """
admin.site.site_header = "Nha Khoa Minh Sinh"
admin.site.site_title = "Nha Khoa Minh Sinh"
admin.site.index_title = "Bảng điều khiển"
"""
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
