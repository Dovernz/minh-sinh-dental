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
                        <iframe id="clinicMap" src="https://maps.google.com/maps?q=123+Ph%E1%BB%91+Hu%E1%BA%BF,+Hai+B%C3%A0+Tr%C6%B0ng,+H%C3%A0+N%E1%BB%99i&t=&z=16&ie=UTF8&iwloc=&output=embed" width="100%" height="200" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
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
.minhsinh-container { width: 92%; max-width: 1320px; margin: 0 auto; }
.booking-header-section { text-align: center; margin-bottom: 30px; }
.booking-main-title { font-size: 28px; font-weight: 700; color: var(--ms-primary); margin-bottom: 8px; }
.booking-sub-title { font-size: 15px; color: var(--ms-text-muted); }

.minhsinh-booking-container { background: #fff; border-radius: 20px; box-shadow: 0 10px 30px -5px rgba(0,0,0,0.06); overflow: hidden; border: 1px solid #e2e8f0; }

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
.booking-body { padding: 36px 40px; min-height: 400px; }
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
.patient-card { background: #fff; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 22px 24px; margin-bottom: 20px; position: relative; transition: 0.3s; }
.patient-card:hover { border-color: var(--ms-primary); box-shadow: 0 8px 25px rgba(0,0,0,0.06); }
.patient-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px dashed var(--ms-border); }
.patient-title { font-weight: 700; color: var(--ms-primary); font-size: 15px; }
.btn-remove-patient { background: #fee2e2; color: #ef4444; border: none; padding: 4px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; font-weight: 600; }
.patient-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px 20px; }
.patient-grid .form-group { margin-bottom: 0; }

/* Form Controls */
.form-group { margin-bottom: 15px; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.form-control { width: 100%; box-sizing: border-box; outline: none; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 14px; padding: 10px 14px; background: #fff; color: var(--ms-text-dark); font-family: inherit; transition: border-color 0.2s, box-shadow 0.2s; }
.form-control:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12); }
textarea.form-control { resize: vertical; min-height: 68px; line-height: 1.5; }
.select-lg { height: 48px; font-weight: 500; }
.error-msg { color: var(--ms-error); font-size: 12px; display: none; margin-top: 4px; }
.has-error .form-control, .form-control.has-error { border-color: var(--ms-error) !important; }
.has-error .error-msg { display: block; }

/* Buttons */
.btn-add-companion { background: var(--ms-primary-light); color: var(--ms-primary); border: 1px dashed var(--ms-primary); padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px; transition: 0.2s; }
.btn-add-companion:hover { background: var(--ms-primary); color: #fff; }
.btn-ms { padding: 12px 28px; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: 0.2s; }
.btn-primary { background: var(--ms-primary); color: #fff; }
.btn-secondary { background: #e2e8f0; color: var(--ms-text-dark); }

/* Time Slots */
.time-slots-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; }
.time-slot { padding: 10px 6px; border: 1px solid var(--ms-border); border-radius: 8px; text-align: center; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.2s ease; }
.time-slot:hover:not(.disabled) { border-color: var(--ms-primary); background: #f0f7ff; }
.time-slot.selected, .time-slot.selected:hover {
    background: #2563eb !important;
    color: #ffffff !important;
    border-color: #2563eb !important;
    box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.3), 0 2px 4px -1px rgba(37, 99, 235, 0.2);
    transform: scale(1.05);
    font-weight: 700 !important;
}
.time-slot.selected div, .time-slot.selected:hover div {
    color: #ffffff !important;
    font-weight: 700 !important;
}
.time-slot.selected .slot-badge-avail, .time-slot.selected:hover .slot-badge-avail {
    color: #dbeafe !important;
    font-weight: 600 !important;
}
.time-slot.disabled { background: #f1f5f9; color: #94a3b8; cursor: not-allowed; border-color: #e2e8f0; opacity: 0.65; pointer-events: none; }
.slot-badge-full { display: block; font-size: 10px; font-weight: 400; color: #ef4444; margin-top: 2px; }
.slot-badge-avail { display: block; font-size: 10px; font-weight: 400; color: #10b981; margin-top: 2px; }
.selected-time-info { margin-top: 14px; padding: 12px 16px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; color: var(--ms-primary); font-size: 14px; }

/* Success */
.success-box { text-align: center; }
.success-icon { width: 64px; height: 64px; background: var(--ms-success); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 20px; }
.group-code-badge { display: inline-block; background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 10px 20px; border-radius: 30px; font-weight: 700; font-size: 18px; margin-bottom: 25px; }
.summary-card { text-align: left; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; }
.summary-item { padding: 10px 0; border-bottom: 1px solid #e2e8f0; }
.summary-item:last-child { border-bottom: none; }
.summary-item strong { color: var(--ms-primary); }

/* Footer Actions */
.booking-footer-actions { display: flex; justify-content: flex-end; align-items: center; gap: 12px; padding: 20px 40px; background: #f8fafc; border-top: 1px solid #e2e8f0; }

/* Responsive Media Queries */
@media (max-width: 640px) {
    .minhsinh-booking-wrapper { padding: 16px 12px; }
    .minhsinh-container { width: 100%; }
    .stepper-wrapper { padding: 14px 12px; }
    .booking-body { padding: 20px 14px; }
    .patient-grid { grid-template-columns: 1fr; gap: 14px; }
    .patient-card { padding: 16px 14px; }
    .btn-ms { width: 100%; padding: 14px; text-align: center; }
    .booking-footer-actions { padding: 16px 14px; flex-direction: column-reverse; gap: 10px; }
}

@media (max-width: 480px) {
    .booking-main-title { font-size: 22px; }
    .clinics-tabs { grid-template-columns: 1fr; }
    .time-slots-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 390px) {
    .booking-main-title { font-size: 20px; }
    .time-slots-grid { grid-template-columns: repeat(2, 1fr); }
}
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

        bookingDateInput.onchange = () => {
            bookingData.date = bookingDateInput.value;
            fetchSlots();
        };

        if (mainServiceSelect) {
            mainServiceSelect.onchange = () => {
                syncFirstPatient();
                fetchSlots();
            };
        }

        fetchClinics();
        fetchServices();
        
        // Mặc định thêm khách hàng đầu tiên
        addPatient(true); 
    }

    // 1. Fetch Dữ liệu
    async function fetchClinics() {
        const fallback = [
            {id: 1, name: "Cơ sở Phố Huế", address: "123 Phố Huế, Hai Bà Trưng, HN", map: "https://maps.google.com/maps?q=123+Ph%E1%BB%91+Hu%E1%BA%BF,+Hai+B%C3%A0+Tr%C6%B0ng,+H%C3%A0+N%E1%BB%99i&t=&z=16&ie=UTF8&iwloc=&output=embed"},
            {id: 2, name: "Cơ sở Nguyễn Trãi", address: "456 Nguyễn Trãi, Thanh Xuân, HN", map: "https://maps.google.com/maps?q=456+Nguy%E1%BB%85n+Tr%C3%A3i,+Thanh+Xu%C3%A2n,+H%C3%A0+N%E1%BB%99i&t=&z=16&ie=UTF8&iwloc=&output=embed"}
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
        mainServiceSelect.innerHTML = '<option value="">-- Đang tải danh sách dịch vụ --</option>';
        try {
            const res = await fetch('/api/services/');
            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {
                    servicesList = data.map(item => ({
                        id: item.category_id,
                        name: item.name,
                        estimate_time: parseInt(item.estimate_time) || 30
                    }));
                }
            }
        } catch (e) {
            console.warn("Lỗi fetch /api/services/, dùng fallback:", e);
        }

        if (!servicesList || servicesList.length === 0) {
            servicesList = [
                {id: 17, name: "ĐIỀU TRỊ TỦY", estimate_time: 60},
                {id: 2, name: "Dịch vụ Nhổ Răng Khôn", estimate_time: 45},
                {id: 18, name: "VỆ SINH - CẠO VÔI RĂNG", estimate_time: 30},
                {id: 27, name: "CẤY GHÉP IMPLANT", estimate_time: 60},
                {id: 1, name: "Dịch vụ Khám & Vệ sinh Răng", estimate_time: 30}
            ];
        }

        mainServiceSelect.innerHTML = '<option value="">-- Vui lòng chọn dịch vụ nha khoa --</option>';
        servicesList.forEach(s => {
            const label = `${s.name} (${s.estimate_time} phút)`;
            mainServiceSelect.innerHTML += `<option value="${s.id}" data-estimate="${s.estimate_time}">${label}</option>`;
        });

        updatePatientServicesDropdown();
    }

    function updatePatientServicesDropdown() {
        document.querySelectorAll(".p-service").forEach(select => {
            const currentVal = select.value || mainServiceSelect.value;
            select.innerHTML = servicesList.map(s => 
                `<option value="${s.id}" data-estimate="${s.estimate_time}" ${s.id == currentVal ? 'selected' : ''}>${s.name} (${s.estimate_time} phút)</option>`
            ).join('');
        });
    }

    function addMinutes(timeStr, mins) {
        if (!timeStr) return "";
        const parts = timeStr.split(':').map(Number);
        const total = (parts[0] || 0) * 60 + (parts[1] || 0) + mins;
        const endH = Math.floor(total / 60) % 24;
        const endM = total % 60;
        return `${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`;
    }

    function displaySelectedTimePreview(startTime, endTime, duration) {
        const grid = document.getElementById("timeSlotsGrid");
        let infoEl = document.getElementById("selectedTimeInfo");
        if (!infoEl && grid) {
            infoEl = document.createElement("div");
            infoEl.id = "selectedTimeInfo";
            infoEl.className = "selected-time-info";
            grid.parentNode.appendChild(infoEl);
        }
        if (infoEl) {
            infoEl.style.display = "block";
            infoEl.innerHTML = `Khung thời gian dự kiến: <strong>${startTime} - ${endTime} (${duration} phút)</strong>`;
        }
    }

    async function fetchSlots() {
        const grid = document.getElementById("timeSlotsGrid");
        grid.innerHTML = '<div class="slot-loading">Đang tải khung giờ khả dụng...</div>';

        const clinicId = bookingData.clinicId || 1;
        const date = bookingData.date || new Date().toISOString().split('T')[0];

        let estimateTime = 30;
        if (mainServiceSelect && mainServiceSelect.selectedIndex > 0) {
            const selectedOpt = mainServiceSelect.options[mainServiceSelect.selectedIndex];
            estimateTime = parseInt(selectedOpt.getAttribute('data-estimate') || '30') || 30;
        }
        const slotsNeeded = Math.ceil(estimateTime / 30);
        const totalPatients = document.querySelectorAll(".patient-card").length || 1;

        let slots = [];
        try {
            const res = await fetch(`/api/available-slots/?clinic_id=${clinicId}&date=${date}`);
            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {
                    slots = data;
                }
            }
        } catch (e) {
            console.warn("Lỗi fetch /api/available-slots/:", e);
        }

        if (slots.length === 0) {
            const fallbackTimes = ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30", "11:00", "11:30", "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00", "17:30", "18:00", "18:30"];
            slots = fallbackTimes.map(t => ({
                time: `${t} - ${addMinutes(t, 30)}`,
                start_time: t,
                available_chairs: 5,
                total_chairs: 5,
                is_full: false
            }));
        }

        grid.innerHTML = "";
        let isCurrentTimeStillValid = false;

        slots.forEach((s, i) => {
            let canBook = true;
            if (i + slotsNeeded > slots.length) {
                canBook = false;
            } else {
                for (let k = 0; k < slotsNeeded; k++) {
                    const checkSlot = slots[i + k];
                    if (!checkSlot || checkSlot.available_chairs < totalPatients || checkSlot.is_full) {
                        canBook = false;
                        break;
                    }
                }
            }

            const isSelected = bookingData.time === s.start_time;
            if (isSelected && canBook) {
                isCurrentTimeStillValid = true;
            }

            const slot = document.createElement("div");
            slot.className = `time-slot ${!canBook ? 'disabled' : ''} ${isSelected && canBook ? 'selected' : ''}`;

            if (!canBook) {
                slot.innerHTML = `<div>${s.start_time}</div><span class="slot-badge-full">Đã kín</span>`;
            } else {
                slot.innerHTML = `<div>${s.start_time}</div><span class="slot-badge-avail">${s.available_chairs} ghế</span>`;
                slot.onclick = () => {
                    document.querySelectorAll(".time-slot").forEach(el => el.classList.remove("selected"));
                    slot.classList.add("selected");
                    bookingData.time = s.start_time;

                    const endTime = addMinutes(s.start_time, estimateTime);
                    bookingData.endTime = endTime;
                    bookingData.duration = estimateTime;

                    displaySelectedTimePreview(s.start_time, endTime, estimateTime);
                    syncFirstPatient();
                };
            }
            grid.appendChild(slot);
        });

        if (bookingData.time && isCurrentTimeStillValid) {
            const endTime = addMinutes(bookingData.time, estimateTime);
            displaySelectedTimePreview(bookingData.time, endTime, estimateTime);
        } else if (bookingData.time && !isCurrentTimeStillValid) {
            bookingData.time = "";
            const infoEl = document.getElementById("selectedTimeInfo");
            if (infoEl) infoEl.style.display = "none";
        }
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
                        <input type="tel" class="form-control p-phone" placeholder="Nhập SĐT (10 - 11 số)" maxlength="11" oninput="this.value = this.value.replace(/\D/g, '').slice(0, 11)">
                    </div>
                    <div class="form-group">
                        <label>Dịch vụ riêng *</label>
                        <select class="form-control p-service" onchange="fetchSlots()">
                            ${servicesList.map(s => `<option value="${s.id}" data-estimate="${s.estimate_time}" ${s.id == mainServiceSelect.value ? 'selected' : ''}>${s.name} (${s.estimate_time} phút)</option>`).join('')}
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
                        <textarea class="form-control p-note" rows="2" placeholder="Triệu chứng, tiền sử hoặc yêu cầu khám riêng..."></textarea>
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
        fetchSlots();
    };

    document.getElementById("btnAddCompanion").onclick = () => {
        addPatient(false);
        fetchSlots();
    };

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
                if (!name.value.trim()) { 
                    name.classList.add("has-error"); 
                    valid = false; 
                } else { 
                    name.classList.remove("has-error"); 
                }
                
                const cleanPhone = phone.value.replace(/\D/g, '').slice(0, 11);
                phone.value = cleanPhone;
                if (!cleanPhone || cleanPhone.length < 10) { 
                    phone.classList.add("has-error"); 
                    valid = false; 
                } else { 
                    phone.classList.remove("has-error"); 
                }
            });
            if (!valid) {
                alert("Vui lòng điền đầy đủ họ tên và số điện thoại hợp lệ (từ 10 đến 11 số)!");
            }
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
            category_id: mainServiceSelect.value,
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
