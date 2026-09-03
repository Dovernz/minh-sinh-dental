document.addEventListener('DOMContentLoaded', function() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file && file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    let container = input.previousElementSibling;
                    let img = null;
                    if (container && container.tagName === 'DIV' && container.querySelector('img')) {
                        img = container.querySelector('img');
                    } else {
                        container = document.createElement('div');
                        container.style.marginBottom = '10px';
                        img = document.createElement('img');
                        img.style.maxHeight = '200px';
                        img.style.borderRadius = '6px';
                        img.style.boxShadow = '0 4px 6px rgba(0,0,0,0.1)';
                        container.appendChild(img);
                        input.parentNode.insertBefore(container, input);
                    }
                    img.src = e.target.result;
                }
                reader.readAsDataURL(file);
            }
        });
    });
});
