document.addEventListener('DOMContentLoaded', () => {
    let debounceTimer;

    // Lắng nghe sự kiện gõ phím trên toàn bộ body, nhưng chỉ kích hoạt nếu thẻ đó là ô search (name="q")
    document.body.addEventListener('input', (e) => {
        if (e.target.name === 'q') {
            clearTimeout(debounceTimer);
            
            debounceTimer = setTimeout(() => {
                const query = e.target.value;
                const url = new URL(window.location.href);
                url.searchParams.set('q', query);
                url.searchParams.delete('p'); // Reset về trang 1

                fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                    .then(response => response.text())
                    .then(html => {
                        const parser = new DOMParser();
                        const doc = parser.parseFromString(html, 'text/html');

                        // Tìm và thay thế ĐÚNG cái form chứa bảng dữ liệu, BỎ QUA thanh search
                        const newTableForm = doc.querySelector('#changelist-form');
                        const currentTableForm = document.querySelector('#changelist-form');
                        
                        if (newTableForm && currentTableForm) {
                            currentTableForm.innerHTML = newTableForm.innerHTML;
                        } else {
                            // Fallback: Nếu không tìm thấy form chuẩn, tìm thẳng thẻ Table
                            const newTable = doc.querySelector('table')?.closest('div');
                            const currentTable = document.querySelector('table')?.closest('div');
                            if (newTable && currentTable) {
                                currentTable.innerHTML = newTable.innerHTML;
                            }
                        }
                        
                        // Đổi URL trên trình duyệt mà không reload
                        window.history.replaceState({}, '', url);
                    })
                    .catch(err => console.error('Live search error:', err));
            }, 300); // 300ms là tốc độ chuẩn nhất
        }
    });
});
