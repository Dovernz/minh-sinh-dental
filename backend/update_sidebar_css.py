file_path = "static/css/admin_custom.css"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove previous CSS targeting the sidebar header image and text
import re
content = re.sub(r'/\* Ép hiển thị lại chữ Nha Khoa Minh Sinh bên cạnh Logo ở Sidebar \*/.*?display: block !important;\n}', '', content, flags=re.DOTALL)

# Append the new precise CSS blocks
new_css = """
/* Ẩn hoàn toàn thẻ <img> bên trong khu vực Sidebar Header */
aside#sidebar header img,
.sidebar-header img,
[data-sidebar] header img {
    display: none !important;
}

/* Ép hiển thị lại dòng chữ Site Header (Nha Khoa Minh Sinh) */
aside#sidebar header a span,
.sidebar-header span,
[data-sidebar] header span {
    display: inline-block !important;
    margin-left: 0 !important;
    font-weight: 700 !important;
    font-size: 1.125rem !important;
    color: #f3f4f6 !important;
}
"""

content += new_css

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content.strip() + "\n")
print("Updated admin_custom.css")
