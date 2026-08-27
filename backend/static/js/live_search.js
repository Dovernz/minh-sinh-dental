document.addEventListener('DOMContentLoaded', () => {
    const searchbar = document.querySelector('input[name="q"]');
    if (!searchbar) return;

    let debounceTimer;
    searchbar.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const query = e.target.value;
            const url = new URL(window.location.href);
            
            if (query) {
                url.searchParams.set('q', query);
            } else {
                url.searchParams.delete('q');
            }
            
            // Giữ lại trang 1 khi search mới
            url.searchParams.delete('p'); 

            fetch(url, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
                .then(response => response.text())
                .then(html => {
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(html, 'text/html');
                    
                    // Thay thế nội dung Form chứa Bảng dữ liệu (Tùy ID của Unfold)
                    const newForm = doc.querySelector('#changelist-form') || (doc.querySelector('form#changelist-search') ? doc.querySelector('form#changelist-search').nextElementSibling : null);
                    const currentForm = document.querySelector('#changelist-form') || (document.querySelector('form#changelist-search') ? document.querySelector('form#changelist-search').nextElementSibling : null);
                    
                    if (newForm && currentForm) {
                        currentForm.innerHTML = newForm.innerHTML;
                    }
                    window.history.replaceState({}, '', url);
                })
                .catch(err => console.error('Live search error:', err));
        }, 300); // Đợi 0.5 giây sau khi ngừng gõ mới search
    });
});
