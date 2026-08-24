(function($) {
    $(document).ready(function() {
        const categorySelect = $('#id_category');
        const serviceSelect = $('#id_service_detail');
        const codeSelect = $('#id_custom_service_code');
        const difficultyInput = $('#id_custom_difficulty');
        const actualPriceInput = $('#id_actual_price');
        const form = actualPriceInput.closest('form');
        
        // Tạo thẻ hiển thị đơn giá nếu chưa có
        if ($('#unit_price_display').length === 0) {
            actualPriceInput.after(' <span id="unit_price_display" style="margin-left: 10px; color: #666; font-weight: bold;"></span>');
        }
        const unitPriceDisplay = $('#unit_price_display');
        
        let servicesData = []; 
        let isProgrammaticChange = false; 

        // Xử lý Input Mask cho actual_price
        function formatPriceInput() {
            let val = actualPriceInput.val().replace(/\D/g, "");
            if (val) {
                actualPriceInput.val(parseInt(val).toLocaleString('en-US'));
            }
        }

        actualPriceInput.on('keyup input', formatPriceInput);
        
        // Trước khi submit, xóa dấu phẩy
        form.on('submit', function() {
            let val = actualPriceInput.val().replace(/\D/g, "");
            actualPriceInput.val(val);
        });

        function populateCodeSelect() {
            codeSelect.empty();
            codeSelect.append(new Option('---------', ''));
            servicesData.forEach(function(s) {
                if (s.code) {
                    codeSelect.append(new Option(s.code, s.service.service_id));
                }
            });
        }

        function populateServiceSelect() {
            const currentSelected = serviceSelect.val();
            serviceSelect.empty();
            serviceSelect.append(new Option('---------', ''));
            servicesData.forEach(function(s) {
                serviceSelect.append(new Option(s.name, s.service.service_id));
            });
            if (currentSelected && serviceSelect.find(`option[value="${currentSelected}"]`).length) {
                serviceSelect.val(currentSelected);
            }
        }

        function updateFieldsFromServiceId(serviceId) {
            if (!serviceId) {
                codeSelect.val('');
                difficultyInput.val('');
                unitPriceDisplay.text('');
                return;
            }
            
            const service = servicesData.find(s => s.service.service_id == serviceId);
            if (service) {
                codeSelect.val(service.code ? service.service_id : '');
                difficultyInput.val(service.difficulty || '');
                if (service.price) {
                    unitPriceDisplay.text('(Đơn giá: ' + parseInt(service.price).toLocaleString('en-US') + ' đ)');
                } else {
                    unitPriceDisplay.text('');
                }
            }
        }

        function loadServices(categoryId, callback) {
            if (!categoryId) {
                servicesData = [];
                populateServiceSelect();
                populateCodeSelect();
                difficultyInput.val('');
                unitPriceDisplay.text('');
                return;
            }

            $.ajax({
                url: '/api/get-services-by-category/',
                data: { 'category_id': categoryId },
                dataType: 'json',
                success: function(data) {
                    servicesData = data;
                    populateServiceSelect();
                    populateCodeSelect();
                    if (callback) callback();
                },
                error: function(err) {
                    console.error('Error fetching services:', err);
                }
            });
        }

        categorySelect.on('change', function() {
            loadServices($(this).val(), function() {
                serviceSelect.val('');
                codeSelect.val('');
                difficultyInput.val('');
                unitPriceDisplay.text('');
            });
        });

        serviceSelect.on('change', function() {
            if (isProgrammaticChange) return;
            isProgrammaticChange = true;
            updateFieldsFromServiceId($(this).val());
            isProgrammaticChange = false;
        });

        codeSelect.on('change', function() {
            if (isProgrammaticChange) return;
            isProgrammaticChange = true;
            
            const selectedId = $(this).val();
            serviceSelect.val(selectedId);
            updateFieldsFromServiceId(selectedId);
            
            isProgrammaticChange = false;
        });

        // Initial Load (Edit page)
        if (categorySelect.val()) {
            const initialServiceId = serviceSelect.val();
            loadServices(categorySelect.val(), function() {
                if (initialServiceId) {
                    serviceSelect.val(initialServiceId);
                    updateFieldsFromServiceId(initialServiceId);
                }
            });
        }
    });
})(django.jQuery);
