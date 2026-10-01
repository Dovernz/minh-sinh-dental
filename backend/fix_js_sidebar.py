import re

with open('/app/static/js/admin_custom.js', 'r', encoding='utf-8') as f:
    content = f.read()

new_logic = '''
// --- FIX SIDEBAR MINI ---
document.addEventListener('DOMContentLoaded', function() {
    let checkSidebar = setInterval(() => {
        let sidebarWrapper = document.querySelector('[x-show="sidebarOpen"]');
        if (sidebarWrapper) {
            clearInterval(checkSidebar);
            
            // Watch for inline style "display: none;" added by Alpine.js
            new MutationObserver((mutations) => {
                mutations.forEach((mutation) => {
                    if (mutation.attributeName === 'style') {
                        if (sidebarWrapper.style.display === 'none') {
                            document.body.classList.add('sidebar-mini');
                        } else {
                            document.body.classList.remove('sidebar-mini');
                        }
                    }
                });
            }).observe(sidebarWrapper, { attributes: true, attributeFilter: ['style'] });
        }
    }, 200);
});
'''

# Append if not already there
if "FIX SIDEBAR MINI" not in content:
    with open('/app/static/js/admin_custom.js', 'a', encoding='utf-8') as f:
        f.write(new_logic)
