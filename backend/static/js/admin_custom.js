(function() {
    function fixUI() {
        let path = window.location.pathname;

        // 1. Việt hóa nút
        document.querySelectorAll('a, button, span').forEach(el => {
            if (el.childNodes.length === 1 && el.textContent.trim() === "Bản ghi nhớ") el.textContent = "Lịch sử thao tác";
        });

        // Nếu ĐANG ở trang chủ thật sự thì không được đổi chữ Bảng điều khiển
        if (path === '/admin/') return; 

        // 2. Định vị Menu đang chọn trên Sidebar
        let activeLink = null, maxLen = 0;
        document.querySelectorAll('aside a').forEach(a => {
            let href = a.getAttribute('href');
            if (href && href !== '/' && path.startsWith(href)) {
                if (href.length > maxLen) { activeLink = a; maxLen = href.length; }
            }
        });

        let urlGroup = new URLSearchParams(window.location.search).get('group');
        let groupName = urlGroup;
        let menuName = activeLink ? activeLink.textContent.trim() : null;

        if (activeLink && !groupName) {
            let ul = activeLink.closest('ul');
            if (ul && ul.previousElementSibling) groupName = ul.previousElementSibling.textContent.trim();
        }

        let displayText = menuName || groupName;
        if (!displayText) return;

        // 3. Đưa "Bảng điều khiển" vào danh sách thanh trừng
        let targets = ['Database', 'Quản lý Database', 'Bảng điều khiển'];

        document.querySelectorAll('nav[aria-label="Breadcrumb"] li').forEach(li => {
            let el = li.querySelector('span, a');
            if (el) {
                let text = el.textContent.trim();
                if (targets.includes(text) || text.startsWith('Welcome')) {
                    if (el.tagName === 'SPAN') {
                        let newA = document.createElement('a');
                        newA.href = groupName ? ('/admin/booking/?group=' + encodeURIComponent(groupName)) : (activeLink ? activeLink.href : '#');
                        newA.className = el.className.replace('text-gray-500', 'text-primary-600 hover:text-primary-700 font-medium');
                        newA.textContent = displayText;
                        li.replaceChild(newA, el);
                    } else {
                        if (el.textContent !== displayText) el.textContent = displayText;
                    }
                }
            }
        });

        let h1 = document.querySelector('h1');
        if (h1) {
            let h1Text = h1.textContent.trim();
            if (targets.includes(h1Text) || h1Text.startsWith('Welcome')) {
                h1.textContent = displayText;
            }
        }

        // 4. Smart Filter cho trang danh mục
        if (path === '/admin/booking/' && groupName) {
            let validUrls = [];
            document.querySelectorAll('aside ul').forEach(ul => {
                if (ul.previousElementSibling && ul.previousElementSibling.textContent.trim() === groupName) {
                    ul.querySelectorAll('a').forEach(a => validUrls.push(a.getAttribute('href')));
                }
            });

            document.querySelectorAll('main a[href^="/admin/booking/"]').forEach(a => {
                let href = a.getAttribute('href');
                if (href && href !== '/admin/booking/') {
                    let isValid = validUrls.some(v => href === v || href.startsWith(v));
                    if (!isValid) {
                        let row = a.closest('tr') || a.closest('div.bg-white > div') || a.closest('.border-b');
                        if (row && row.style.display !== 'none') row.style.display = 'none';
                    }
                }
            });
        }
    }

    let observer = new MutationObserver(fixUI);
    let startObserve = setInterval(() => {
        if (document.body) {
            fixUI();
            observer.observe(document.body, { childList: true, subtree: true });
            clearInterval(startObserve);
        }
    }, 50);
})();