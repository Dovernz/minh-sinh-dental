document.addEventListener("DOMContentLoaded", function() {
    var wordFileInput = document.getElementById('id_word_file');
    if (wordFileInput) {
        wordFileInput.addEventListener('change', function(e) {
            var file = e.target.files[0];
            if (!file) return;

            // Only process .docx files
            if (file.name.indexOf('.docx') === -1) {
                return;
            }

            var formData = new FormData();
            formData.append('file', file);

            // Optional: show some loading state
            var titleInput = document.getElementById('id_title');
            if (titleInput && !titleInput.value) {
                titleInput.value = "Đang trích xuất...";
            }

            fetch('/api/parse-docx/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Set title
                    if (titleInput) {
                        titleInput.value = data.title;
                    }

                    // Set slug if prepopulated field JS is not triggering
                    var slugInput = document.getElementById('id_slug');
                    if (slugInput && !slugInput.value && data.slug) { slugInput.value = data.slug; }

                    // Set content in Rich Text Editor
                    const contentHtml = data.content;
                    
                    // 1. Thử với CKEditor
                    if (typeof CKEDITOR !== 'undefined' && CKEDITOR.instances['id_content']) {
                        CKEDITOR.instances['id_content'].setData(contentHtml);
                    }
                    // 2. Thử với TinyMCE
                    else if (typeof tinymce !== 'undefined' && tinymce.get('id_content')) {
                        tinymce.get('id_content').setContent(contentHtml);
                    }
                    // 3. Thử với Summernote (jQuery)
                    else if (typeof jQuery !== 'undefined' && jQuery('#id_content').summernote) {
                        jQuery('#id_content').summernote('code', contentHtml);
                    }
                    // 4. Fallback cho Textarea mặc định
                    else {
                        const contentField = document.getElementById('id_content');
                        if (contentField) {
                            contentField.value = contentHtml;
                            // Kích hoạt event change để các editor ẩn tự đồng bộ
                            contentField.dispatchEvent(new Event('change', { bubbles: true }));
                        }
                    }
                } else {
                    alert("Lỗi bóc tách Word: " + data.message);
                    if (titleInput && titleInput.value === "Đang trích xuất...") {
                        titleInput.value = "";
                    }
                }
            })
            .catch(error => {
                console.error("Lỗi gọi API bóc tách:", error);
                alert("Lỗi gọi API bóc tách Word!");
                if (titleInput && titleInput.value === "Đang trích xuất...") {
                    titleInput.value = "";
                }
            });
        });
    }
});
