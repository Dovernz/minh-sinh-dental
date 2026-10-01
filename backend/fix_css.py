css_append = '''
/* --- DARK MODE PURPLE OVERRIDE --- */
html.dark, html[data-theme="dark"] {
    --color-primary-50: rgb(250, 245, 255) !important;
    --color-primary-100: rgb(243, 232, 255) !important;
    --color-primary-200: rgb(233, 213, 255) !important;
    --color-primary-300: rgb(216, 180, 254) !important;
    --color-primary-400: rgb(192, 132, 252) !important;
    --color-primary-500: rgb(168, 85, 247) !important;
    --color-primary-600: rgb(147, 51, 234) !important;
    --color-primary-700: rgb(126, 34, 206) !important;
    --color-primary-800: rgb(107, 33, 168) !important;
    --color-primary-900: rgb(88, 28, 135) !important;
    --color-primary-950: rgb(59, 7, 100) !important;
}

/* --- Tùy chỉnh Sidebar Mini --- */
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
body.sidebar-mini #nav-sidebar span, 
body.sidebar-mini #nav-sidebar h3 {
    display: none !important;
}
'''

with open('/app/static/css/admin_custom.css', 'a', encoding='utf-8') as f:
    f.write(css_append)
