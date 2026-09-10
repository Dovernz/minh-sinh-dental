(function() {
    function fixUI() {

    // --- XÂY DỰNG KHUNG DASHBOARD TỔNG QUAN ---
    if (window.location.pathname === '/admin/') {
        // 1. Giấu thông báo báo lỗi phân quyền mặc định của Django
        document.querySelectorAll('*').forEach(el => {
            if (el.childNodes.length === 1 && (el.textContent.includes('Bạn không có quyền xem') || el.textContent.includes('permission to view'))) {
                let alertBox = el.closest('.border-red-500') || el.closest('div[class*="bg-red"]') || el;
                if (alertBox) alertBox.style.display = 'none';
            }
        });

        // 2. Chèn Khung Thống kê vào cột trái (Giữ nguyên cột Hoạt động gần đây bên phải)
        if (!document.getElementById('custom-dashboard-wrapper')) {
            let main = document.querySelector('main');
            if (main) {
                // Tìm cột nội dung chính bên trái của Unfold
                let flexContainer = main.querySelector('.flex.flex-col') || main.firstElementChild;
                if (flexContainer) {
                    let leftCol = flexContainer.firstElementChild;
                    if (leftCol && leftCol.tagName === 'DIV') {
                        let dashHTML = `
                        <div id="custom-dashboard-wrapper" class="mb-8 w-full">
                            <h2 class="text-xl font-bold mb-4 text-gray-800 dark:text-gray-200">Tổng quan Hệ thống</h2>
                            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                                <div class="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-5 shadow-sm">
                                    <h3 class="text-gray-500 text-sm font-medium mb-2">Doanh thu hôm nay</h3>
                                    <p class="text-2xl font-bold text-primary-600">0 VNĐ</p>
                                </div>
                                <div class="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-5 shadow-sm">
                                    <h3 class="text-gray-500 text-sm font-medium mb-2">Lịch hẹn mới</h3>
                                    <p class="text-2xl font-bold text-green-600">0</p>
                                </div>
                                <div class="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-5 shadow-sm">
                                    <h3 class="text-gray-500 text-sm font-medium mb-2">Khách hàng mới</h3>
                                    <p class="text-2xl font-bold text-orange-600">0</p>
                                </div>
                            </div>
                            <div class="bg-white dark:bg-gray-900 rounded-md border border-gray-200 dark:border-gray-800 p-8 shadow-sm flex flex-col items-center justify-center min-h-[300px]">
                                <svg class="w-16 h-16 text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path></svg>
                                <p class="text-gray-500 text-lg font-medium">Bảng điều khiển đã sẵn sàng!</p>
                                <p class="text-gray-400 text-sm mt-2">Khu vực này đã được làm sạch để tích hợp Biểu đồ Thống kê thực tế.</p>
                            </div>
                        </div>
                        `;
                        leftCol.insertAdjacentHTML('afterbegin', dashHTML);
                    }
                }
            }
        }
    }
    

        // Quét riêng khu vực Sidebar (aside) để giấu cục Database an toàn
        document.querySelectorAll('aside').forEach(aside => {
            aside.querySelectorAll('h3, span, div, p').forEach(el => {
                if (el.childNodes.length === 1 && (el.textContent.trim() === 'Database' || el.textContent.trim() === 'Quản lý Database')) {
                    // Tìm thẻ bao bọc (Wrapper) của tiêu đề này
                    let wrapper = el.closest('li') || el.closest('div.mt-8') || el.parentElement;
                    if (wrapper) wrapper.style.display = 'none';

                    // Nếu danh sách <ul> nằm tách rời bên dưới, giấu luôn nó
                    let next = el.nextElementSibling || (wrapper ? wrapper.nextElementSibling : null);
                    if (next && next.tagName === 'UL') next.style.display = 'none';
                }
            });
        });
    
        // 1. TRIỆT TIÊU TẬN GỐC MENU "DATABASE" TRÊN SIDEBAR
        document.querySelectorAll('aside nav ul').forEach(ul => {
            let titleNode = ul.previousElementSibling;
            if (titleNode && (titleNode.textContent.trim() === 'Database' || titleNode.textContent.trim() === 'Quản lý Database')) {
                titleNode.style.display = 'none'; // Giấu tiêu đề nhóm
                ul.style.display = 'none'; // Giấu danh sách con
                ul.classList.add('ignore-scan'); // Gắn cờ để JS bên dưới không quét nhầm vào đây nữa
            }
        });

        let path = window.location.pathname;
        let urlParams = new URLSearchParams(window.location.search);
        let groupName = urlParams.get('group');

        // 2. Việt hóa nút
        document.querySelectorAll('a, button, span').forEach(el => {
            if (el.childNodes.length === 1 && el.textContent.trim() === "Bản ghi nhớ") el.textContent = "Lịch sử thao tác";
        });

        // 3. Tự động tra ngược tên nhóm từ Sidebar (Tuyệt đối bỏ qua nhóm đã giấu)
        if (!groupName && path !== '/admin/') {
            let maxLen = 0;
            document.querySelectorAll('aside ul:not(.ignore-scan) a').forEach(a => {
                let href = a.getAttribute('href');
                if (href && href !== '/' && path.startsWith(href)) {
                    if (href.length > maxLen) {
                        let ul = a.closest('ul');
                        if (ul && ul.previousElementSibling) {
                            groupName = ul.previousElementSibling.textContent.trim();
                            maxLen = href.length;
                        }
                    }
                }
            });
        }

        // 4. Ghi đè Breadcrumb & Tiêu đề H1
        if (groupName) {
            let targets = ['Database', 'Quản lý Database', 'Booking', 'Bảng điều khiển'];

            document.querySelectorAll('nav[aria-label="Breadcrumb"] li').forEach(li => {
                let el = li.querySelector('span, a');
                if (el) {
                    let text = el.textContent.trim();
                    if (targets.includes(text) || text.startsWith('Welcome')) {
                        if (el.tagName === 'SPAN') {
                            let newA = document.createElement('a');
                            newA.href = '/admin/booking/?group=' + encodeURIComponent(groupName);
                            newA.className = 'text-primary-600 hover:text-primary-700 font-medium';
                            newA.textContent = groupName;
                            li.replaceChild(newA, el);
                        } else {
                            if (el.textContent !== groupName) el.textContent = groupName;
                            el.href = '/admin/booking/?group=' + encodeURIComponent(groupName);
                            el.style.pointerEvents = 'auto';
                        }
                    }
                }
            });

            let h1 = document.querySelector('h1');
            if (h1 && (targets.includes(h1.textContent.trim()) || h1.textContent.trim().startsWith('Welcome'))) {
                h1.textContent = groupName;
            }
        }
    }

    fixUI();
    let observer = new MutationObserver(fixUI);
    let checkBody = setInterval(() => {
        if (document.body) {
            observer.observe(document.body, { childList: true, subtree: true });
            clearInterval(checkBody);
        }
    }, 50);
})();

// Vòng lặp Brute-force: Tiêu diệt cục Database mỗi 100ms để chống lại Alpine.js
setInterval(() => {
    document.querySelectorAll('aside span, aside div, aside h3').forEach(el => {
        let text = el.textContent.trim();
        if (el.childNodes.length === 1 && (text === 'Database' || text === 'Quản lý Database')) {
            let li = el.closest('li');
            if (li) {
                li.style.display = 'none';
            } else {
                let wrapper = el.parentElement;
                if (wrapper) {
                    wrapper.style.display = 'none';
                    if(wrapper.nextElementSibling && wrapper.nextElementSibling.tagName === 'UL') {
                        wrapper.nextElementSibling.style.display = 'none';
                    }
                }
            }
        }
    });
}, 100);
    