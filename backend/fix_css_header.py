file_path = "static/css/admin_custom.css"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Remove the old hiding block
old_block = """/* Hide logo in sidebar, only keep it for login page */
#sidebar header img,
.sidebar-header img,
.sidebar img[alt="Nha Khoa Minh Sinh"] {
    display: none !important;
}"""

content = content.replace(old_block, "").strip()

new_block = """
/* Ép hiển thị lại chữ Nha Khoa Minh Sinh bên cạnh Logo ở Sidebar */
aside#sidebar header a span,
.sidebar-header span,
[data-sidebar] header span {
    display: inline-block !important;
    margin-left: 12px;
    font-weight: 700;
    font-size: 1.125rem;
    color: #f3f4f6; /* Màu trắng xám cho Dark Mode */
}
/* Căn chỉnh Logo và Text nằm ngang hàng */
aside#sidebar header a,
.sidebar-header a {
    display: flex !important;
    align-items: center !important;
}
/* Đảm bảo Logo giữ nguyên kích thước nhỏ, bo tròn */
aside#sidebar header img {
    height: 36px !important;
    width: 36px !important;
    object-fit: cover;
    border-radius: 9999px; /* Bo tròn */
    display: block !important;
}
"""

content = content + "\n" + new_block

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
