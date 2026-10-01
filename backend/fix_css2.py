import re

with open('/app/static/css/admin_custom.css', 'r', encoding='utf-8') as f:
    content = f.read()

# Xóa bỏ khối CSS "Tùy chỉnh Sidebar Mini" cũ
idx = content.find('/* --- Tùy chỉnh Sidebar Mini --- */')
if idx != -1:
    content = content[:idx]

css_append = '''/* --- Tùy chỉnh Sidebar Mini --- */
body.sidebar-mini [x-show="sidebarOpen"] {
    display: block !important;
    width: 80px !important;
}
body.sidebar-mini #nav-sidebar {
    width: 80px !important;
}
body.sidebar-mini #nav-sidebar-inner {
    overflow-x: hidden;
}

/* Ẩn các thành phần thừa khi thu gọn */
body.sidebar-mini #nav-sidebar h2, 
body.sidebar-mini [x-on\\:click="$dispatch('opencommand')"], 
body.sidebar-mini .flex-col.select-none,
body.sidebar-mini .material-symbols-outlined.ml-auto {
    display: none !important;
}

/* Xử lý text và icon trong thẻ a của menu */
body.sidebar-mini #nav-sidebar-apps ol li a {
    font-size: 0 !important; 
    justify-content: center !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}
body.sidebar-mini #nav-sidebar-apps ol li a span.material-symbols-outlined,
body.sidebar-mini #nav-sidebar-apps ol li a svg {
    font-size: 20px !important;
    margin-right: 0 !important;
    margin-left: 0 !important;
}

/* Fix Branding Logo */
body.sidebar-mini .navigation_header > div {
    font-size: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
    justify-content: center !important;
    margin-left: 0 !important;
}
body.sidebar-mini .navigation_header img {
    margin: 0 auto;
}
'''

with open('/app/static/css/admin_custom.css', 'w', encoding='utf-8') as f:
    f.write(content + css_append)
