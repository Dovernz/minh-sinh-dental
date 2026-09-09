
document.addEventListener("DOMContentLoaded", function() {
    // Quét các nút bấm và thay thế text sang ngôn ngữ tự nhiên hơn
    document.querySelectorAll('a, button').forEach(el => {
        if (el.textContent.includes("Bản ghi nhớ")) {
            el.innerHTML = el.innerHTML.replace("Bản ghi nhớ", "Lịch sử thao tác");
        }
    });
});
