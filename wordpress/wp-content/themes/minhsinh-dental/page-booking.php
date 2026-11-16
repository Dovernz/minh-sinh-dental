<?php 
/* Template Name: Trang Đặt Lịch Hẹn Cao Cấp */ 
get_header(); 
?>

<div class="minhsinh-booking-wrapper">
    <div class="minhsinh-container">
        <!-- Tiêu đề trang -->
        <div class="booking-header-section">
            <h1 class="booking-main-title">Đặt Lịch Khám Nha Khoa</h1>
            <p class="booking-sub-title">Chăm sóc nụ cười của bạn cùng đội ngũ chuyên gia Nha khoa Minh Sinh</p>
        </div>

        <!-- Booking Container -->
        <div class="minhsinh-booking-container" id="minhsinhBookingApp">
            
            <!-- 1. Thanh Stepper 4 bước -->
            <div class="stepper-wrapper">
                <div class="step-item active" data-step="1">
                    <div class="step-counter">1</div>
                    <div class="step-name">Dịch vụ & Cơ sở</div>
                </div>
                <div class="step-item" data-step="2">
                    <div class="step-counter">2</div>
                    <div class="step-name" id="step2Name">Thời gian & Bác sĩ</div>
                </div>
                <div class="step-item" data-step="3">
                    <div class="step-counter">3</div>
                    <div class="step-name">Thông tin Khách hàng</div>
                </div>
                <div class="step-item" data-step="4">
                    <div class="step-counter">4</div>
                    <div class="step-name">Hoàn tất</div>
                </div>
            </div>

            <!-- Form Body -->
            <div class="booking-body">
                
                <!-- BƯỚC 1: Chọn Dịch vụ & Cơ sở -->
                <div class="booking-step-pane active" id="paneStep1">
                    <h3 class="pane-title">Lựa chọn cơ sở nha khoa</h3>
                    <div class="clinics-tabs" id="clinicsTabs">
                        <div class="clinic-loading">Đang tải danh sách cơ sở...</div>
                    </div>

                    <div class="map-container">
                        <iframe id="clinicMap" src="" width="100%" height="200" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
                    </div>

                    <h3 class="pane-title" style="margin-top: 24px;">Chọn Dịch Vụ Nha Khoa</h3>
                    <div class="form-group">
                        <select class="form-control select-lg" id="mainServiceSelect">
                            <option value="">-- Đang tải danh sách dịch vụ --</option>
                        </select>
                        <span class="error-msg" id="errMainService">Vui lòng chọn dịch vụ.</span>
                    </div>
                </div>

                <!-- BƯỚC 2: Chọn Thời gian & Bác sĩ -->
                <div class="booking-step-pane" id="paneStep2">
                    <div id="doctorSelectionSection">
                        <h3 class="pane-title">Chọn Bác Sĩ Điều Trị</h3>
                        <div class="doctors-grid" id="doctorsGrid">
                            <!-- Rendered by JS -->
                        </div>
                    </div>

                    <h3 class="pane-title" style="margin-top: 24px;">Chọn Ngày & Khung Giờ Khám</h3>
                    <div class="datetime-picker-wrapper">
                        <div class="form-group">
                            <label for="bookingDate">Ngày khám <span class="required">*</span></label>
                            <input type="date" id="bookingDate" class="form-control">
                        </div>
                        <div class="form-group">
                            <label>Khung giờ <span class="required">*</span></label>
                            <div class="time-slots-grid" id="timeSlotsGrid">
                                <div class="slot-loading">Vui lòng chọn ngày để xem giờ...</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- BƯỚC 3: Điền Thông tin Khách hàng (Multi-Customer) -->
                <div class="booking-step-pane" id="paneStep3">
                    <div class="pane-header-flex">
                        <h3 class="pane-title">Thông tin người khám</h3>
                        <button type="button" class="btn-add-companion" id="btnAddCompanion">
                            <span class="icon">+</span> Thêm người đi cùng
                        </button>
                    </div>
                    
                    <div id="patientsListContainer">
                        <!-- Patient Cards will be injected here -->
                    </div>
                </div>

                <!-- BƯỚC 4: Hoàn tất Đặt lịch -->
                <div class="booking-step-pane" id="paneStep4">
                    <div class="success-box" id="successBox">
                        <div class="success-icon">✓</div>
                        <h3>Đặt Lịch Thành Công!</h3>
                        <p>Cảm ơn quý khách đã tin tưởng Nha khoa Minh Sinh.</p>
                        
                        <div class="group-code-badge" id="displayGroupCode">Mã nhóm: MS-GRP-XXXX</div>
                        
                        <div class="summary-card">
                            <h4>Chi tiết lịch hẹn:</h4>
                            <div id="summaryList" class="summary-list">
                                <!-- Dynamic review data -->
                            </div>
                        </div>
                        <p style="margin-top: 20px; font-size: 13px; color: var(--ms-text-muted);">
                            Nhân viên tư vấn sẽ liên hệ lại với quý khách trong vòng 15 phút để xác nhận.
                        </p>
                    </div>
                </div>

            </div>

            <!-- Footer Action Buttons -->
            <div class="booking-footer-actions">
                <button type="button" class="btn-ms btn-secondary" id="btnPrev" style="display: none;">Quay lại</button>
                <button type="button" class="btn-ms btn-primary" id="btnNext">Tiếp tục</button>
            </div>

        </div>
    </div>
</div>

<style>
:root {
    --ms-primary: #2563eb;
    --ms-primary-dark: #1d4ed8;
    --ms-primary-light: #eff6ff;
    --ms-text-dark: #1e293b;
    --ms-text-muted: #64748b;
    --ms-border: #cbd5e1;
    --ms-bg: #f8fafc;
    --ms-error: #ef4444;
    --ms-success: #22c55e;
}

.minhsinh-booking-wrapper { background-color: var(--ms-bg); padding: 40px 15px; font-family: 'Inter', sans-serif; color: var(--ms-text-dark); }
.minhsinh-container { max-width: 850px; margin: 0 auto; }
.booking-header-section { text-align: center; margin-bottom: 30px; }
.booking-main-title { font-size: 28px; font-weight: 700; color: var(--ms-primary); margin-bottom: 8px; }
.booking-sub-title { font-size: 15px; color: var(--ms-text-muted); }

.minhsinh-booking-container { background: #fff; border-radius: 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.05); overflow: hidden; border: 1px solid #e2e8f0; }

/* Stepper */
.stepper-wrapper { display: flex; justify-content: space-between; background: var(--ms-primary-light); padding: 20px 30px; border-bottom: 1px solid #e2e8f0; }
.step-item { display: flex; align-items: center; gap: 10px; opacity: 0.4; transition: 0.3s; }
.step-item.active { opacity: 1; }
.step-item.completed { opacity: 0.8; }
.step-counter { width: 28px; height: 28px; background: #cbd5e1; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 13px; }
.step-item.active .step-counter, .step-item.completed .step-counter { background: var(--ms-primary); }
.step-name { font-size: 13.5px; font-weight: 600; display: none; }
@media(min-width: 768px) { .step-name { display: block; } }

/* Body */
.booking-body { padding: 30px; min-height: 400px; }
.booking-step-pane { display: none; animation: fadeIn 0.4s ease; }
.booking-step-pane.active { display: block; }
@keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
.pane-title { font-size: 18px; font-weight: 700; margin-bottom: 18px; color: var(--ms-text-dark); }
.pane-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }

/* Clinics */
.clinics-tabs { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; margin-bottom: 15px; }
.clinic-tab-btn { text-align: left; background: #fff; border: 2px solid var(--ms-border); padding: 12px; border-radius: 10px; cursor: pointer; transition: 0.2s; }
.clinic-tab-btn.active { border-color: var(--ms-primary); background: var(--ms-primary-light); }
.clinic-tab-btn strong { display: block; font-size: 14px; }
.clinic-address-text { font-size: 12px; color: var(--ms-text-muted); }

/* Multi-Patient Cards */
.patient-card { background: #fff; border: 1px solid var(--ms-border); border-radius: 12px; padding: 20px; margin-bottom: 20px; position: relative; transition: 0.3s; }
.patient-card:hover { border-color: var(--ms-primary); box-shadow: 0 5px 15px rgba(0,0,0,0.05); }
.patient-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; padding-bottom: 10px; border-bottom: 1px dashed var(--ms-border); }
.patient-title { font-weight: 700; color: var(--ms-primary); font-size: 15px; }
.btn-remove-patient { background: #fee2e2; color: #ef4444; border: none; padding: 4px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; font-weight: 600; }
.patient-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }
@media(max-width: 600px) { .patient-grid { grid-template-columns: 1fr; } }

/* Form Controls */
.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.form-control { width: 100%; padding: 10px 12px; border: 1px solid var(--ms-border); border-radius: 8px; font-size: 14px; transition: 0.2s; }
.form-control:focus { border-color: var(--ms-primary); outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1); }
.select-lg { height: 48px; font-weight: 500; }
.error-msg { color: var(--ms-error); font-size: 12px; display: none; margin-top: 4px; }
.has-error .form-control { border-color: var(--ms-error); }
.has-error .error-msg { display: block; }

/* Buttons */
.btn-add-companion { background: var(--ms-primary-light); color: var(--ms-primary); border: 1px dashed var(--ms-primary); padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px; transition: 0.2s; }
.btn-add-companion:hover { background: var(--ms-primary); color: #fff; }
.btn-ms { padding: 12px 28px; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: 0.2s; }
.btn-primary { background: var(--ms-primary); color: #fff; }
.btn-secondary { background: #e2e8f0; color: var(--ms-text-dark); }

/* Time Slots */
.time-slots-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; }
.time-slot { padding: 10px; border: 1px solid var(--ms-border); border-radius: 8px; text-align: center; cursor: pointer; font-size: 13px; font-weight: 600; }
.time-slot.selected { background: var(--ms-primary); color: #fff; border-color: var(--ms-primary); }
.time-slot.disabled { background: #f1f5f9; color: #94a3b8; cursor: not-allowed; }

/* Success */
.success-box { text-align: center; }
.success-icon { width: 64px; height: 64px; background: var(--ms-success); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 20px; }
.group-code-badge { display: inline-block; background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 10px 20px; border-radius: 30px; font-weight: 700; font-size: 18px; margin-bottom: 25px; }
.summary-card { text-align: left; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; }
.summary-item { padding: 10px 0; border-bottom: 1px solid #e2e8f0; }
.summary-item:last-child { border-bottom: none; }
.summary-item strong { color: var(--ms-primary); }
</style>

<script>
document.addEventListener("DOMContentLoaded", function () {
    // --- CẤU HÌNH ---
    const SHOW_DOCTOR_SELECTION = false; // Đổi thành true để hiện chọn bác sĩ

    const bookingData = {
        clinicId: "",
        clinicName: "",
        date: "",
        time: "", // Giờ chung từ bước 2
        patients: [] // Danh sách khách hàng
    };

    let servicesList = []; // Lưu cache dịch vụ
    let currentStep = 1;

    // DOM Elements
    const btnNext = document.getElementById("btnNext");
    const btnPrev = document.getElementById("btnPrev");
    const patientsContainer = document.getElementById("patientsListContainer");
    const mainServiceSelect = document.getElementById("mainServiceSelect");
    const bookingDateInput = document.getElementById("bookingDate");

    // Khởi tạo
    init();

    function init() {
        if (!SHOW_DOCTOR_SELECTION) {
            document.getElementById("doctorSelectionSection").style.display = "none";
            document.getElementById("step2Name").innerText = "Chọn Thời Gian Khám";
        }

        // Thiết lập ngày tối thiểu là hôm nay
        const today = new Date().toISOString().split('T')[0];
        bookingDateInput.min = today;
        bookingDateInput.value = today;
        bookingData.date = today;

        fetchClinics();
        fetchServices();
        
        // Mặc định thêm khách hàng đầu tiên
        addPatient(true); 
    }

    // 1. Fetch Dữ liệu
    async function fetchClinics() {
        const fallback = [
            {id: 1, name: "Cơ sở Phố Huế", address: "123 Phố Huế, Hai Bà Trưng, HN", map: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3724.096811983057!2d105.85289997689973!3d21.028811480620556!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135ab9bd98319f7%3A0x9d4a8e235e16ef90!2zMTIzIFBo4buRIEh14bq_!5e0!3m2!1svi!2s!4v1700000000000"},
            {id: 2, name: "Cơ sở Nguyễn Trãi", address: "456 Nguyễn Trãi, Thanh Xuân, HN", map: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3724.677708579737!2d105.8030044768992!3d21.004818980637175!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135ac80b741031b%3A0x3f3d35091a13e54b!2zNDU2IE5ndXnhu4VuIFRyw6Fp!5e0!3m2!1svi!2s!4v1700000000000"}
        ];
        renderClinics(fallback);
    }

    function renderClinics(clinics) {
        const container = document.getElementById("clinicsTabs");
        container.innerHTML = "";
        clinics.forEach((c, idx) => {
            const btn = document.createElement("div");
            btn.className = `clinic-tab-btn ${idx === 0 ? 'active' : ''}`;
            btn.innerHTML = `<strong>${c.name}</strong><span class="clinic-address-text">${c.address}</span>`;
            if(idx === 0) {
                bookingData.clinicId = c.id;
                bookingData.clinicName = c.name;
                document.getElementById("clinicMap").src = c.map;
            }
            btn.onclick = () => {
                document.querySelectorAll(".clinic-tab-btn").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
                bookingData.clinicId = c.id;
                bookingData.clinicName = c.name;
                document.getElementById("clinicMap").src = c.map;
                fetchSlots();
            };
            container.appendChild(btn);
        });
        fetchSlots();
    }

    async function fetchServices() {
        const fallback = [
            {id: 1, name: "Khám & Tư vấn tổng quát", price: "Miễn phí"},
            {id: 2, name: "Cạo vôi răng siêu âm", price: "200.000đ"},
            {id: 3, name: "Tẩy trắng răng Laser", price: "1.500.000đ"},
            {id: 4, name: "Niềng răng thẩm mỹ", price: "Từ 25tr"}
        ];
        servicesList = fallback;
        mainServiceSelect.innerHTML = '<option value="">-- Vui lòng chọn dịch vụ nha khoa --</option>';
        fallback.forEach(s => {
            mainServiceSelect.innerHTML += `<option value="${s.id}">${s.name} - ${s.price}</option>`;
        });
    }

    function fetchSlots() {
        const grid = document.getElementById("timeSlotsGrid");
        grid.innerHTML = "";
        const times = ["08:00", "09:00", "10:00", "11:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00"];
        times.forEach(t => {
            const slot = document.createElement("div");
            slot.className = "time-slot";
            slot.innerText = t;
            slot.onclick = () => {
                document.querySelectorAll(".time-slot").forEach(s => s.classList.remove("selected"));
                slot.classList.add("selected");
                bookingData.time = t;
            };
            grid.appendChild(slot);
        });
    }

    // 2. Quản lý Multi-Patient
    function addPatient(isFirst = false) {
        const pId = Date.now();
        const patientHtml = `
            <div class="patient-card" id="patient-${pId}" data-id="${pId}">
                <div class="patient-card-header">
                    <span class="patient-title">${isFirst ? 'Khách hàng #1 (Người liên hệ chính)' : 'Khách hàng tiếp theo (Người đi cùng)'}</span>
                    ${!isFirst ? `<button type="button" class="btn-remove-patient" onclick="removePatient(${pId})">✕ Xóa</button>` : ''}
                </div>
                <div class="patient-grid">
                    <div class="form-group">
                        <label>Họ và tên *</label>
                        <input type="text" class="form-control p-name" placeholder="Nhập họ tên">
                    </div>
                    <div class="form-group">
                        <label>Số điện thoại *</label>
                        <input type="tel" class="form-control p-phone" placeholder="Nhập SĐT">
                    </div>
                    <div class="form-group">
                        <label>Dịch vụ riêng *</label>
                        <select class="form-control p-service">
                            ${servicesList.map(s => `<option value="${s.id}" ${s.id == mainServiceSelect.value ? 'selected' : ''}>${s.name}</option>`).join('')}
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Giờ khám riêng *</label>
                        <select class="form-control p-time">
                            ${generateTimeOptions()}
                        </select>
                    </div>
                    <div class="form-group" style="grid-column: 1/-1">
                        <label>Ghi chú</label>
                        <input type="text" class="form-control p-note" placeholder="Triệu chứng hoặc yêu cầu...">
                    </div>
                </div>
            </div>
        `;
        patientsContainer.insertAdjacentHTML('beforeend', patientHtml);
        
        // Nếu là khách đầu tiên, đồng bộ dịch vụ và giờ từ bước 1 & 2
        if(isFirst) {
            const card = document.getElementById(`patient-${pId}`);
            card.querySelector('.p-service').value = mainServiceSelect.value;
            card.querySelector('.p-time').value = bookingData.time || "08:00";
        }
    }

    window.removePatient = function(id) {
        document.getElementById(`patient-${id}`).remove();
    };

    document.getElementById("btnAddCompanion").onclick = () => addPatient(false);

    function generateTimeOptions() {
        let options = "";
        for (let h = 8; h <= 19; h++) {
            let hh = h < 10 ? '0' + h : h;
            options += `<option value="${hh}:00" ${bookingData.time === hh+':00' ? 'selected' : ''}>${hh}:00</option>`;
            if(h !== 19) options += `<option value="${hh}:30" ${bookingData.time === hh+':30' ? 'selected' : ''}>${hh}:30</option>`;
        }
        return options;
    }

    // 3. Điều hướng & Validation
    btnNext.onclick = () => {
        if (validateStep(currentStep)) {
            if (currentStep < 4) {
                currentStep++;
                if(currentStep === 3) syncFirstPatient();
                if(currentStep === 4) submitBooking();
                updateUI();
            }
        }
    };

    btnPrev.onclick = () => {
        if (currentStep > 1) {
            currentStep--;
            updateUI();
        }
    };

    function validateStep(step) {
        if (step === 1) {
            if (!mainServiceSelect.value) {
                mainServiceSelect.parentElement.classList.add("has-error");
                return false;
            }
            mainServiceSelect.parentElement.classList.remove("has-error");
            return true;
        }
        if (step === 2) {
            if (!bookingData.time) { alert("Vui lòng chọn khung giờ khám!"); return false; }
            return true;
        }
        if (step === 3) {
            let valid = true;
            const cards = document.querySelectorAll(".patient-card");
            cards.forEach(card => {
                const name = card.querySelector(".p-name");
                const phone = card.querySelector(".p-phone");
                if (!name.value.trim()) { name.classList.add("has-error"); valid = false; }
                else name.classList.remove("has-error");
                if (phone.value.length < 10) { phone.classList.add("has-error"); valid = false; }
                else phone.classList.remove("has-error");
            });
            return valid;
        }
        return true;
    }

    function syncFirstPatient() {
        const firstCard = patientsContainer.querySelector(".patient-card");
        if(firstCard) {
            firstCard.querySelector(".p-service").value = mainServiceSelect.value;
            firstCard.querySelector(".p-time").value = bookingData.time;
        }
    }

    function updateUI() {
        document.querySelectorAll(".booking-step-pane").forEach((p, i) => {
            p.classList.toggle("active", i + 1 === currentStep);
        });
        document.querySelectorAll(".step-item").forEach((s, i) => {
            s.classList.toggle("active", i + 1 === currentStep);
            s.classList.toggle("completed", i + 1 < currentStep);
        });
        btnPrev.style.display = (currentStep > 1 && currentStep < 4) ? "block" : "none";
        btnNext.innerText = currentStep === 3 ? "Xác nhận Đặt lịch" : "Tiếp tục";
        if(currentStep === 4) btnNext.style.display = "none";
    }

    // 4. Submit API
    async function submitBooking() {
        const patients = [];
        document.querySelectorAll(".patient-card").forEach(card => {
            patients.push({
                fullName: card.querySelector(".p-name").value,
                phone: card.querySelector(".p-phone").value,
                category_id: card.querySelector(".p-service").value,
                start_time: card.querySelector(".p-time").value,
                note: card.querySelector(".p-note").value
            });
        });

        const payload = {
            clinic_id: bookingData.clinicId,
            date: bookingData.date,
            start_time: bookingData.time,
            patients: patients
        };

        console.log("Sending Payload:", payload);

        let generatedCode = 'MS-GRP-' + new Date().toISOString().slice(0, 10).replace(/-/g, '') + '-' + Math.floor(1000 + Math.random() * 9000);
        try {
            const response = await fetch('/api/bookings/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (response.ok) {
                const resData = await response.json();
                if (resData.group_code) generatedCode = resData.group_code;
                else if (resData.booking_code) generatedCode = resData.booking_code;
            }
        } catch (error) {
            console.warn('Backend Django chưa sẵn sàng, dùng mã dự phòng:', error);
        }
        const displayGroupCode = document.getElementById('displayGroupCode');
        if (displayGroupCode) displayGroupCode.innerText = 'Mã nhóm: ' + generatedCode;
        let summaryHtml = `<div class="summary-item"><strong>Cơ sở:</strong> ${bookingData.clinicName} | <strong>Ngày:</strong> ${bookingData.date}</div>`;
        patients.forEach((p, idx) => {
            const sName = servicesList.find(s => s.id == p.category_id)?.name || 'Dịch vụ nha khoa';
            summaryHtml += `<div class="summary-item"><strong>Khách ${idx+1}:</strong> ${p.fullName} - ${p.phone}<br><small>Dịch vụ: ${sName} | Giờ: ${p.start_time}</small></div>`;
        });
        document.getElementById('summaryList').innerHTML = summaryHtml;
    }
});
</script>

<?php get_footer(); ?>
