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
                        
                        <div class="group-code-badge" id="displayGroupCode">Mã đặt chỗ: MS-GRP-XXXX</div>
                        
                        <div class="summary-card">
                            <h4>Chi tiết lịch hẹn:</h4>
                            <div id="summaryList" class="summary-list">
                                <!-- Dynamic review data -->
                            </div>
                        </div>

                        <!-- 2 Nút thêm vào lịch -->
                        <div class="calendar-actions">
                            <button type="button" class="btn-calendar btn-calendar-ics" id="btnDownloadIcs">
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
                                <span>Thêm vào lịch</span>
                            </button>
                            <a href="#" target="_blank" rel="noopener noreferrer" class="btn-calendar btn-calendar-google" id="btnGoogleCalendar">
                                <svg width="18" height="18" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/></svg>
                                <span>Google Calendar</span>
                            </a>
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
.minhsinh-container { width: 92%; max-width: 1320px; margin: 0 auto; box-sizing: border-box; }
.booking-header-section { text-align: center; margin-bottom: 30px; }
.booking-main-title { font-size: 28px; font-weight: 700; color: var(--ms-primary); margin-bottom: 8px; }
.booking-sub-title { font-size: 15px; color: var(--ms-text-muted); }

.minhsinh-booking-container { background: #fff; border-radius: 20px; box-shadow: 0 10px 30px -5px rgba(0,0,0,0.06); overflow: hidden; border: 1px solid #e2e8f0; box-sizing: border-box; }

/* Stepper */
.stepper-wrapper { display: flex; justify-content: space-between; background: var(--ms-primary-light); padding: 20px 30px; border-bottom: 1px solid #e2e8f0; box-sizing: border-box; }
.step-item { display: flex; align-items: center; gap: 10px; opacity: 0.4; transition: 0.3s; }
.step-item.active { opacity: 1; }
.step-item.completed { opacity: 0.8; }
.step-counter { width: 28px; height: 28px; background: #cbd5e1; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 600; font-size: 13px; flex-shrink: 0; }
.step-item.active .step-counter, .step-item.completed .step-counter { background: var(--ms-primary); }
.step-name { font-size: 13.5px; font-weight: 600; display: none; }
@media(min-width: 768px) { .step-name { display: block; } }

/* Body */
.booking-body { padding: 36px 40px; min-height: 400px; box-sizing: border-box; }
.booking-step-pane { display: none; opacity: 1; box-sizing: border-box; }
.booking-step-pane.active { display: block; opacity: 1; }
.pane-title { font-size: 18px; font-weight: 700; margin-bottom: 18px; color: var(--ms-text-dark); }
.pane-header-flex { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; flex-wrap: wrap; gap: 10px; }

/* Clinics */
.clinics-tabs { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 12px; margin-bottom: 15px; }
.clinic-tab-btn { text-align: left; background: #fff; border: 2px solid var(--ms-border); padding: 12px; border-radius: 10px; cursor: pointer; transition: 0.2s; box-sizing: border-box; }
.clinic-tab-btn.active { border-color: var(--ms-primary); background: var(--ms-primary-light); }
.clinic-tab-btn strong { display: block; font-size: 14px; }
.clinic-address-text { font-size: 12px; color: var(--ms-text-muted); }

/* Multi-Patient Cards */
.patient-card { background: #fff; border: 1.5px solid #e2e8f0; border-radius: 14px; padding: 22px 24px; margin-bottom: 20px; position: relative; transition: 0.3s; box-sizing: border-box; }
.patient-card:hover { border-color: var(--ms-primary); box-shadow: 0 8px 25px rgba(0,0,0,0.06); }
.patient-card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px dashed var(--ms-border); flex-wrap: wrap; gap: 10px; }
.patient-title { font-weight: 700; color: var(--ms-primary); font-size: 15px; }
.btn-remove-patient { background: #fee2e2; color: #ef4444; border: none; padding: 4px 10px; border-radius: 6px; font-size: 12px; cursor: pointer; font-weight: 600; }
.patient-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px 20px; }
.patient-grid .form-group { margin-bottom: 0; }

/* Form Controls */
.form-group { margin-bottom: 15px; box-sizing: border-box; }
.form-group label { display: block; font-size: 13px; font-weight: 600; margin-bottom: 6px; }
.form-control { width: 100%; box-sizing: border-box; outline: none; border: 1.5px solid #cbd5e1; border-radius: 8px; font-size: 14px; padding: 10px 14px; background: #fff; color: var(--ms-text-dark); font-family: inherit; transition: border-color 0.2s, box-shadow 0.2s; }
.form-control:focus { border-color: #2563eb; outline: none; box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.12); }
textarea.form-control { resize: vertical; min-height: 68px; line-height: 1.5; }
.select-lg { height: 48px; font-weight: 500; }
.error-msg { color: var(--ms-error); font-size: 12px; display: none; margin-top: 4px; }
.has-error .form-control, .form-control.has-error { border-color: var(--ms-error) !important; }
.has-error .error-msg { display: block; }
.name-input-error {
    border-color: #ef4444 !important;
    background-color: #fef2f2 !important;
}
.name-error-msg {
    color: #ef4444 !important;
    font-size: 11.5px !important;
    line-height: 1.4 !important;
    margin-top: 4px !important;
    margin-bottom: 0 !important;
    font-weight: 500 !important;
    display: flex !important;
    align-items: center !important;
    gap: 4px !important;
}
.name-error-msg .warning-icon {
    font-size: 11px !important;
    line-height: 1 !important;
    flex-shrink: 0 !important;
}

/* Buttons */
.btn-add-companion { background: var(--ms-primary-light); color: var(--ms-primary); border: 1px dashed var(--ms-primary); padding: 8px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 13px; transition: 0.2s; box-sizing: border-box; }
.btn-add-companion:hover { background: var(--ms-primary); color: #fff; }
.btn-ms { padding: 12px 28px; border-radius: 8px; font-weight: 600; cursor: pointer; border: none; transition: background-color 0.2s, transform 0.15s; box-sizing: border-box; opacity: 1; }
.btn-primary { background: #2563eb; color: #ffffff; opacity: 1; }
.btn-primary:hover:not(:disabled) { background: #1d4ed8; opacity: 1; }
.btn-ms:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary { background: #e2e8f0; color: var(--ms-text-dark); opacity: 1; }

/* Time Slots */
.time-slots-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr)); gap: 10px; box-sizing: border-box; }
.time-slot { padding: 10px 6px; border: 1px solid var(--ms-border); border-radius: 8px; text-align: center; cursor: pointer; font-size: 13px; font-weight: 600; transition: all 0.2s ease; box-sizing: border-box; }
.time-slot:hover:not(.disabled) { border-color: var(--ms-primary); background: #f0f7ff; }
.time-slot.selected, .time-slot.selected:hover {
    background: #1e40af !important;
    color: #ffffff !important;
    border: 2px solid #3b82f6 !important;
    box-shadow: 0 4px 14px rgba(30, 64, 175, 0.45) !important;
    transform: scale(1.05);
    font-weight: 700 !important;
}
.time-slot.selected div, .time-slot.selected:hover div {
    color: #ffffff !important;
    font-weight: 700 !important;
}
.time-slot.selected .slot-badge-avail, .time-slot.selected:hover .slot-badge-avail {
    color: #bfdbfe !important;
    font-weight: 600 !important;
}
.time-slot.disabled { background: #f1f5f9; color: #94a3b8; cursor: not-allowed; border-color: #e2e8f0; opacity: 0.65; pointer-events: none; }
.time-slot.disabled.past-slot { background: #f1f5f9; color: #94a3b8; opacity: 0.6; }
.slot-badge-full { display: block; font-size: 10px; font-weight: 400; color: #ef4444; margin-top: 2px; }
.slot-badge-avail { display: block; font-size: 10px; font-weight: 400; color: #10b981; margin-top: 2px; }
.slot-badge-past { display: block; font-size: 10px; font-weight: 400; color: #94a3b8; margin-top: 2px; }
.selected-time-info { margin-top: 14px; padding: 12px 16px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 8px; color: var(--ms-primary); font-size: 14px; box-sizing: border-box; }

/* Success */
.success-box { text-align: center; box-sizing: border-box; }
.success-icon { width: 64px; height: 64px; background: var(--ms-success); color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 32px; margin: 0 auto 20px; }
.group-code-badge { display: inline-block; background: #f0fdf4; color: #166534; border: 1px solid #bbf7d0; padding: 10px 20px; border-radius: 30px; font-weight: 700; font-size: 18px; margin-bottom: 25px; box-sizing: border-box; }
.summary-card { text-align: left; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-sizing: border-box; }
.summary-item { padding: 10px 0; border-bottom: 1px solid #e2e8f0; box-sizing: border-box; word-break: break-word; }
.summary-item:last-child { border-bottom: none; }
.summary-item strong { color: var(--ms-primary); }

/* Footer Actions */
.booking-footer-actions { display: flex; justify-content: flex-end; align-items: center; gap: 12px; padding: 20px 40px; background: #f8fafc; border-top: 1px solid #e2e8f0; box-sizing: border-box; }

/* Responsive Media Queries (Fluid Responsive cho PC >= 1280px, Tablet 768-1024px, Mobile 375-414px) */
@media (max-width: 1024px) {
    .minhsinh-container { width: 95%; max-width: 100%; }
    .booking-body { padding: 28px 30px; }
}

@media (max-width: 768px) {
    .minhsinh-booking-wrapper { padding: 20px 10px; }
    .minhsinh-container { width: 100%; }
    .stepper-wrapper { padding: 16px 15px; }
    .booking-body { padding: 24px 20px; }
    .patient-grid { grid-template-columns: 1fr; gap: 14px; }
    .patient-card { padding: 18px 16px; }
    .booking-footer-actions { padding: 16px 20px; }
}

@media (max-width: 414px) {
    .minhsinh-booking-wrapper { padding: 12px 8px; }
    .stepper-wrapper { padding: 12px 10px; }
    .booking-body { padding: 18px 12px; }
    .patient-card { padding: 14px 12px; }
    .btn-ms { width: 100%; padding: 12px; text-align: center; }
    .booking-footer-actions { padding: 14px 12px; flex-direction: column-reverse; gap: 10px; }
    .booking-main-title { font-size: 22px; }
    .clinics-tabs { grid-template-columns: 1fr; }
    .time-slots-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 375px) {
    .time-slots-grid { grid-template-columns: repeat(2, 1fr); }
    .booking-main-title { font-size: 20px; }
}

/* Calendar & Success UI enhancements */
.minhsinh-booking-container { border-radius: 10px !important; }
.patient-card { border-radius: 10px !important; }
.summary-card { border-radius: 10px !important; }
.group-code-badge { border-radius: 8px !important; }
.btn-ms { border-radius: 8px !important; }
.clinic-tab-btn { border-radius: 8px !important; }
.calendar-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
    margin-top: 20px;
    flex-wrap: wrap;
    box-sizing: border-box;
}
.btn-calendar {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 10px 18px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    border: 1.5px solid transparent;
    transition: all 0.2s ease;
    box-sizing: border-box;
}
.btn-calendar-ics {
    background: #0284c7;
    color: #ffffff !important;
}
.btn-calendar-ics:hover {
    background: #0369a1;
    color: #ffffff !important;
}
.btn-calendar-google {
    background: #ffffff;
    color: #1e293b !important;
    border-color: #cbd5e1;
}
.btn-calendar-google:hover {
    background: #f8fafc;
    border-color: #94a3b8;
    color: #0f172a !important;
}

</style>

<script>
document.addEventListener("DOMContentLoaded", function () {

    const NAME_INVALID_REGEX = /[^\p{L}\s]/u;
    const NAME_WARNING_MSG = "⚠️ Họ và tên chỉ được chứa chữ cái và dấu cách, không chứa số hoặc ký tự đặc biệt.";

    function validateNameField(inputEl) {
        const val = inputEl.value;
        let errEl = inputEl.parentNode.querySelector(".name-error-msg");
        if (NAME_INVALID_REGEX.test(val)) {
            inputEl.classList.add("name-input-error");
            if (!errEl) {
                errEl = document.createElement("p");
                errEl.className = "name-error-msg";
                inputEl.parentNode.appendChild(errEl);
            }
            errEl.innerHTML = '<span class="warning-icon">⚠️</span><span>Họ và tên chỉ được chứa chữ cái và dấu cách, không chứa số hoặc ký tự đặc biệt.</span>';
            return false;
        } else {
            inputEl.classList.remove("name-input-error");
            if (errEl) {
                errEl.remove();
            }
            return true;
        }
    }

    // Real-time handler: Cho phép gõ tự do, cảnh báo khi có số/ký tự đặc biệt
    document.addEventListener("input", function(e) {
        if (e.target && e.target.classList.contains("p-name")) {
            validateNameField(e.target);
        }
        if (e.target && e.target.classList.contains("p-phone")) {
            e.target.value = e.target.value.replace(/\D/g, "").slice(0, 11);
        }
    }, true);

    // Event delegation cho thay đổi giờ khám riêng của từng khách (.p-time)
    document.addEventListener("change", function(e) {
        if (e.target && e.target.classList.contains("p-time")) {
            refreshAllPatientTimeSelects();
        }
    }, true);

    // Lắng nghe sự kiện 'ms:capacityDistributed' từ booking-capacity.js
    document.addEventListener('ms:capacityDistributed', function(e) {
        refreshAllPatientTimeSelects();
    });

    // --- CẤU HÌNH ---
    const SHOW_DOCTOR_SELECTION = false; // Đổi thành true để hiện chọn bác sĩ

    const bookingData = {
        clinicId: "",
        clinicName: "",
        date: "",
        time: "", // Giờ chung từ bước 2
        patients: [] // Danh sách khách hàng
    };
    window.__msBookingData = bookingData;

    let servicesList = []; // Lưu cache dịch vụ
    let currentStep = 1;
    let currentSlots = []; // Lưu toàn cục danh sách slots từ fetchSlots

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
        const today = new Date();
        const todayStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
        bookingDateInput.min = todayStr;
        bookingDateInput.value = todayStr;
        bookingData.date = todayStr;

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

    // Helper (e): Kiểm tra khung giờ đã qua so với giờ hiện tại của ngày hôm nay
    function isPastTimeSlot(slotTime, selectedDate) {
        if (!slotTime || !selectedDate) return false;
        const now = new Date();
        const todayStr = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
        
        if (selectedDate < todayStr) return true;
        if (selectedDate > todayStr) return false;
        
        // selectedDate === todayStr
        const [slotH, slotM] = slotTime.split(':').map(Number);
        const slotTotalMins = (slotH || 0) * 60 + (slotM || 0);
        const currentTotalMins = now.getHours() * 60 + now.getMinutes();
        
        return slotTotalMins <= currentTotalMins;
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
            btn.dataset.clinicId = c.id;
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
        if (window.MSBookingCapacity) window.MSBookingCapacity.sync(bookingData);
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

        // Lưu currentSlots toàn cục phục vụ cho refreshAllPatientTimeSelects
        currentSlots = slots;

        grid.innerHTML = "";
        let firstValidSlotTime = null;
        let isCurrentTimeStillValid = false;

        slots.forEach((s, i) => {
            const isPast = isPastTimeSlot(s.start_time, bookingData.date);
            const isFullOrNoChairs = s.is_full === true || s.available_chairs <= 0;
            
            // Yêu cầu b & d: KHÔNG disable các khung giờ chỉ vì available_chairs < totalPatients 
            // (nếu slot còn ít nhất 1 ghế và chưa qua giờ hiện tại, vẫn cho chọn)
            let canBook = true;
            if (isPast || isFullOrNoChairs) {
                canBook = false;
            }

            if (canBook && !firstValidSlotTime) {
                firstValidSlotTime = s.start_time;
            }

            const isSelected = bookingData.time === s.start_time;
            if (isSelected && canBook) {
                isCurrentTimeStillValid = true;
            }

            const slot = document.createElement("div");
            slot.className = `time-slot ${!canBook ? 'disabled' : ''} ${isPast ? 'past-slot' : ''} ${isSelected && canBook ? 'selected' : ''}`;
            slot.dataset.time = s.start_time;

            if (isPast) {
                slot.setAttribute('aria-disabled', 'true');
                slot.innerHTML = `<div>${s.start_time}</div><span class="slot-badge-past">Đã qua</span>`;
            } else if (isFullOrNoChairs) {
                slot.setAttribute('aria-disabled', 'true');
                slot.innerHTML = `<div>${s.start_time}</div><span class="slot-badge-full">Hết chỗ</span>`;
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
                    
                    // Gọi tự động phân bổ nếu cần khi đổi slot
                    autoDistributePatientsIfNeeded();
                };
            }
            grid.appendChild(slot);
        });

        // Yêu cầu e: Nếu bookingData.time đang chọn đã qua hoặc hết ghế, tự động chuyển sang slot hợp lệ đầu tiên chưa qua và còn ghế
        if (bookingData.time) {
            const currentSlotObj = slots.find(s => s.start_time === bookingData.time);
            const isCurrentPast = isPastTimeSlot(bookingData.time, bookingData.date);
            const isCurrentFull = currentSlotObj ? (currentSlotObj.is_full || currentSlotObj.available_chairs <= 0) : true;
            
            if (isCurrentPast || isCurrentFull || !isCurrentTimeStillValid) {
                if (firstValidSlotTime) {
                    bookingData.time = firstValidSlotTime;
                    const newSelectedEl = grid.querySelector(`.time-slot[data-time="${firstValidSlotTime}"]`);
                    if (newSelectedEl) {
                        document.querySelectorAll(".time-slot").forEach(el => el.classList.remove("selected"));
                        newSelectedEl.classList.add("selected");
                    }
                    const endTime = addMinutes(bookingData.time, estimateTime);
                    displaySelectedTimePreview(bookingData.time, endTime, estimateTime);
                    syncFirstPatient();
                } else {
                    bookingData.time = "";
                    const infoEl = document.getElementById("selectedTimeInfo");
                    if (infoEl) infoEl.style.display = "none";
                }
            } else {
                const endTime = addMinutes(bookingData.time, estimateTime);
                displaySelectedTimePreview(bookingData.time, endTime, estimateTime);
            }
        } else if (!bookingData.time && firstValidSlotTime) {
            // Nếu chưa chọn giờ nào, có thể chọn mặc định slot đầu tiên hợp lệ
            bookingData.time = firstValidSlotTime;
            const newSelectedEl = grid.querySelector(`.time-slot[data-time="${firstValidSlotTime}"]`);
            if (newSelectedEl) {
                document.querySelectorAll(".time-slot").forEach(el => el.classList.remove("selected"));
                newSelectedEl.classList.add("selected");
            }
            const endTime = addMinutes(bookingData.time, estimateTime);
            displaySelectedTimePreview(bookingData.time, endTime, estimateTime);
            syncFirstPatient();
        }

        // Cập nhật lại dropdown giờ của các khách
        refreshAllPatientTimeSelects();
        
        // Gọi auto distribute sau khi fetch slots xong nếu cần
        autoDistributePatientsIfNeeded();
    }

    // Yêu cầu b: Hàm autoDistributePatientsIfNeeded()
    function autoDistributePatientsIfNeeded() {
        const autoDistributeToggle = window.MSBookingCapacity && typeof window.MSBookingCapacity.getAutoDistribute === 'function' 
            ? window.MSBookingCapacity.getAutoDistribute() 
            : true; // Mặc định bật hoặc theo trạng thái UI

        const patientCards = document.querySelectorAll(".patient-card");
        const totalPatients = patientCards.length;
        if (totalPatients === 0 || !bookingData.time) return;

        // Tìm slot hiện tại của bookingData.time trong currentSlots
        const currentSlotIndex = currentSlots.findIndex(s => s.start_time === bookingData.time);
        if (currentSlotIndex === -1) return;

        const currentSlot = currentSlots[currentSlotIndex];
        const availableChairsInMain = currentSlot ? currentSlot.available_chairs : 0;

        // Điều kiện auto-distribute: số khách > 5 hoặc số khách > số ghế trống của bookingData.time (và autoDistribute đang bật)
        if (autoDistributeToggle && (totalPatients > 5 || totalPatients > availableChairsInMain)) {
            let assignedCount = 0;
            
            for (let i = currentSlotIndex; i < currentSlots.length; i++) {
                const slot = currentSlots[i];
                if (isPastTimeSlot(slot.start_time, bookingData.date) || slot.is_full || slot.available_chairs <= 0) {
                    continue;
                }

                const capacity = slot.available_chairs;
                const canTake = Math.min(capacity, totalPatients - assignedCount);

                for (let c = 0; c < canTake; c++) {
                    if (assignedCount < totalPatients) {
                        const targetCard = patientCards[assignedCount];
                        const timeSelect = targetCard.querySelector('.p-time');
                        if (timeSelect) {
                            timeSelect.value = slot.start_time;
                        }
                        assignedCount++;
                    }
                }

                if (assignedCount >= totalPatients) break;
            }

            // Nếu vẫn còn khách chưa được phân bổ (do thiếu slot), phân bổ phần còn lại vào slot hợp lệ cuối cùng tìm được
            if (assignedCount < totalPatients) {
                let lastValidSlotTime = bookingData.time;
                for (let i = currentSlots.length - 1; i >= 0; i--) {
                    if (!isPastTimeSlot(currentSlots[i].start_time, bookingData.date) && !currentSlots[i].is_full) {
                        lastValidSlotTime = currentSlots[i].start_time;
                        break;
                    }
                }
                for (let i = assignedCount; i < totalPatients; i++) {
                    const timeSelect = patientCards[i].querySelector('.p-time');
                    if (timeSelect) {
                        timeSelect.value = lastValidSlotTime;
                    }
                }
            }

            // Cập nhật lại giao diện các select time sau khi distribute
            refreshAllPatientTimeSelects();
        }
    }

    // Yêu cầu c: Viết hàm refreshAllPatientTimeSelects()
    function refreshAllPatientTimeSelects() {
        const patientCards = document.querySelectorAll(".patient-card");
        
        patientCards.forEach(card => {
            const timeSelect = card.querySelector('.p-time');
            if (!timeSelect) return;

            const currentSelectedVal = timeSelect.value;
            let optionsHtml = "";

            if (!currentSlots || currentSlots.length === 0) {
                // Fallback nếu chưa có currentSlots
                for (let h = 8; h <= 19; h++) {
                    let hh = h < 10 ? '0' + h : h;
                    const t1 = `${hh}:00`;
                    const t2 = `${hh}:30`;
                    [t1, t2].forEach(t => {
                        const isPast = isPastTimeSlot(t, bookingData.date);
                        if (!isPast) {
                            optionsHtml += `<option value="${t}" ${currentSelectedVal === t ? 'selected' : ''}>${t} (5 ghế trống)</option>`;
                        } else {
                            optionsHtml += `<option value="${t}" disabled ${currentSelectedVal === t ? 'selected' : ''}>${t} (Đã qua)</option>`;
                        }
                    });
                }
            } else {
                currentSlots.forEach(slot => {
                    const t = slot.start_time;
                    const isPast = isPastTimeSlot(t, bookingData.date);
                    
                    // Tính số ghế đã bị các .patient-card KHÁC trong cùng nhóm chiếm ở khung giờ t
                    let occupiedByOthers = 0;
                    patientCards.forEach(otherCard => {
                        if (otherCard !== card) {
                            const otherTimeSelect = otherCard.querySelector('.p-time');
                            if (otherTimeSelect && otherTimeSelect.value === t) {
                                occupiedByOthers++;
                            }
                        }
                    });

                    const slotAvailableChairs = slot.available_chairs !== undefined ? slot.available_chairs : 5;
                    const slotIsFull = slot.is_full === true;
                    const rem = Math.max(0, slotAvailableChairs - occupiedByOthers);

                    let disabledAttr = "";
                    let textLabel = "";

                    if (isPast) {
                        // Nếu isPastTimeSlot(t, bookingData.date): option.disabled = true, text = `${t} (Đã qua)` — TUYỆT ĐỐI KHÔNG hiển thị số lượng slot/ghế.
                        disabledAttr = "disabled";
                        textLabel = `${t} (Đã qua)`;
                    } else if (rem <= 0 || slotIsFull) {
                        // Nếu !isPast && (rem <= 0 || slotIsFull): option.disabled = true, text = `${t} (Hết chỗ)`.
                        disabledAttr = "disabled";
                        textLabel = `${t} (Hết chỗ)`;
                    } else {
                        // Nếu !isPast && rem > 0: option.disabled = false, text = `${t} (${rem} ghế trống)`.
                        disabledAttr = "";
                        textLabel = `${t} (${rem} ghế trống)`;
                    }

                    const isSelected = currentSelectedVal === t ? "selected" : "";
                    optionsHtml += `<option value="${t}" ${disabledAttr} ${isSelected}>${textLabel}</option>`;
                });
            }

            timeSelect.innerHTML = optionsHtml;

            // Đảm bảo nếu giá trị đang chọn bị disabled thì tự động chuyển sang option hợp lệ đầu tiên chưa disabled
            if (timeSelect.selectedOptions.length === 0 || timeSelect.selectedOptions[0].disabled) {
                const firstEnabledOpt = timeSelect.querySelector("option:not([disabled])");
                if (firstEnabledOpt) {
                    timeSelect.value = firstEnabledOpt.value;
                }
            }
        });
    }

    // Yêu cầu a: reindexPatients() và cập nhật tiêu đề Khách 1, Khách 2, Khách 3...
    function reindexPatients() {
        const patientCards = document.querySelectorAll(".patient-card");
        patientCards.forEach((card, idx) => {
            const titleEl = card.querySelector(".patient-title");
            const removeBtnHtml = idx > 0 ? `<button type="button" class="btn-remove-patient" onclick="removePatient(${card.dataset.id})">✕ Xóa</button>` : '';
            const headerFlex = card.querySelector(".patient-card-header");
            
            const guestNumber = idx + 1;
            const guestLabel = guestNumber === 1 ? `Khách ${guestNumber} (Người liên hệ chính)` : `Khách ${guestNumber}`;
            
            if (titleEl) {
                titleEl.innerText = guestLabel;
            }
            
            // Cập nhật lại nút xóa (chỉ từ khách 2 trở đi mới có nút xóa)
            const existingRemoveBtn = headerFlex.querySelector(".btn-remove-patient");
            if (idx === 0) {
                if (existingRemoveBtn) existingRemoveBtn.remove();
            } else {
                if (!existingRemoveBtn) {
                    headerFlex.insertAdjacentHTML('beforeend', `<button type="button" class="btn-remove-patient" onclick="removePatient(${card.dataset.id})">✕ Xóa</button>`);
                }
            }
        });
    }

    // 2. Quản lý Multi-Patient
    function addPatient(isFirst = false) {
        const pId = Date.now() + Math.floor(Math.random() * 1000);
        const currentCount = document.querySelectorAll(".patient-card").length;
        const guestNumber = currentCount + 1;
        const guestLabel = isFirst ? `Khách ${guestNumber} (Người liên hệ chính)` : `Khách ${guestNumber}`;

        const patientHtml = `
            <div class="patient-card" id="patient-${pId}" data-id="${pId}">
                <div class="patient-card-header">
                    <span class="patient-title">${guestLabel}</span>
                    ${!isFirst ? `<button type="button" class="btn-remove-patient" onclick="removePatient(${pId})">✕ Xóa</button>` : ''}
                </div>
                <div class="patient-grid">
                    <div class="form-group">
                        <label>Họ và tên *</label>
                        <input type="text" class="form-control p-name" placeholder="Nhập họ tên" maxlength="50">
                    </div>
                    <div class="form-group">
                        <label>Số điện thoại *</label>
                        <input type="tel" class="form-control p-phone" placeholder="Nhập SĐT (10 - 11 số)" maxlength="11" inputmode="numeric" oninput="this.value = this.value.replace(/\D/g, '').slice(0, 11)">
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
        
        reindexPatients();

        // Nếu là khách đầu tiên, đồng bộ dịch vụ và giờ từ bước 1 & 2
        if(isFirst) {
            const card = document.getElementById(`patient-${pId}`);
            if (card) {
                card.querySelector('.p-service').value = mainServiceSelect.value;
                card.querySelector('.p-time').value = bookingData.time || "08:00";
            }
        }

        refreshAllPatientTimeSelects();
    }

    window.removePatient = function(id) {
        const cardEl = document.getElementById(`patient-${id}`);
        if (cardEl) {
            cardEl.remove();
            reindexPatients();
            fetchSlots();
            refreshAllPatientTimeSelects();
            if (window.MSBookingCapacity) window.MSBookingCapacity.sync(bookingData);
        }
    };

    document.getElementById("btnAddCompanion").onclick = () => {
        addPatient(false);
        fetchSlots();
        autoDistributePatientsIfNeeded();
        if (window.MSBookingCapacity) window.MSBookingCapacity.sync(bookingData);
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
                if(currentStep === 3) {
                    syncFirstPatient();
                    autoDistributePatientsIfNeeded();
                }
                if(currentStep === 4) submitBooking();
                updateUI();
                if (window.MSBookingCapacity) window.MSBookingCapacity.sync(bookingData);
            }
        }
    };

    btnPrev.onclick = () => {
        if (currentStep > 1) {
            currentStep--;
            updateUI();
            if (window.MSBookingCapacity) window.MSBookingCapacity.sync(bookingData);
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
            let hasNameError = false;
            const cards = document.querySelectorAll(".patient-card");
            cards.forEach(card => {
                const name = card.querySelector(".p-name");
                const phone = card.querySelector(".p-phone");
                
                const isNameValid = validateNameField(name);
                const trimmedName = name.value.trim();

                if (!trimmedName || !isNameValid || trimmedName.length < 2) { 
                    name.classList.add("name-input-error");
                    if (!isNameValid) {
                        hasNameError = true;
                    }
                    valid = false; 
                } else { 
                    name.classList.remove("name-input-error"); 
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
                if (hasNameError) {
                    alert(NAME_WARNING_MSG);
                } else {
                    alert("Vui lòng điền đầy đủ họ tên và số điện thoại hợp lệ (từ 10 đến 11 số)!");
                }
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
        refreshAllPatientTimeSelects();
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
        btnNext.disabled = false;
        btnNext.style.opacity = "1";
        if(currentStep === 4) btnNext.style.display = "none";
    }

    // 4. Submit API
    
    function downloadIcsCalendar(booking) {
        const title = "Khám răng tại Nha Khoa Minh Sinh";
        const loc = booking.clinicName.includes("Hồ Chí Minh") || booking.clinicName.includes("Lê Hồng Phong")
            ? "456 Lê Hồng Phong, P.1, Q.10, TP.HCM"
            : "123 Phố Huế, Q. Hai Bà Trưng, Hà Nội";
        const desc = `Khám răng tại Nha Khoa Minh Sinh.\nMã đặt chỗ: ${booking.groupCode}\nCơ sở: ${loc}\nThời gian: ${booking.time} ngày ${booking.date}`;
        const [startH, startM] = (booking.time || "09:00").split(':').map(Number);
        const dateParts = (booking.date || "2026-11-20").split('-');
        const y = dateParts[0], m = dateParts[1], d = dateParts[2];
        const dtStart = `${y}${m}${d}T${String(startH).padStart(2,'0')}${String(startM).padStart(2,'0')}00`;
        let endH = startH + 1;
        if (endH >= 24) endH = 23;
        const dtEnd = `${y}${m}${d}T${String(endH).padStart(2,'0')}${String(startM).padStart(2,'0')}00`;
        
        const icsLines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Minh Sinh Dental//Booking Portal//VI",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            `UID:minhsinh-${booking.groupCode}-${Date.now()}@minhsinhdental.com`,
            `DTSTAMP:${dtStart}Z`,
            `DTSTART:${dtStart}`,
            `DTEND:${dtEnd}`,
            `SUMMARY:${title}`,
            `DESCRIPTION:${desc}`,
            `LOCATION:${loc}`,
            "STATUS:CONFIRMED",
            "END:VEVENT",
            "END:VCALENDAR"
        ];
        
        const blob = new Blob([icsLines.join("\r\n")], { type: "text/calendar;charset=utf-8" });
        const a = document.createElement("a");
        a.href = window.URL.createObjectURL(blob);
        a.download = `lich_kham_${booking.groupCode}.ics`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    function setupCalendarButtons(booking) {
        const btnIcs = document.getElementById("btnDownloadIcs");
        const btnGoogle = document.getElementById("btnGoogleCalendar");
        
        if (btnIcs) {
            btnIcs.onclick = function() {
                downloadIcsCalendar(booking);
            };
        }
        
        if (btnGoogle) {
            const title = encodeURIComponent("Khám răng tại Nha Khoa Minh Sinh");
            const loc = encodeURIComponent(booking.clinicName.includes("Hồ Chí Minh") || booking.clinicName.includes("Lê Hồng Phong")
                ? "456 Lê Hồng Phong, P.1, Q.10, TP.HCM"
                : "123 Phố Huế, Q. Hai Bà Trưng, Hà Nội");
            const desc = encodeURIComponent(`Khám răng tại Nha Khoa Minh Sinh.
Mã đặt chỗ: ${booking.groupCode}
Cơ sở: ${booking.clinicName}
Thời gian: ${booking.time} ngày ${booking.date}`);
            const dateParts = (booking.date || "2026-11-20").split('-');
            const [startH, startM] = (booking.time || "09:00").split(':').map(Number);
            const dtStart = `${dateParts[0]}${dateParts[1]}${dateParts[2]}T${String(startH).padStart(2,'0')}${String(startM).padStart(2,'0')}00`;
            let endH = startH + 1;
            if (endH >= 24) endH = 23;
            const dtEnd = `${dateParts[0]}${dateParts[1]}${dateParts[2]}T${String(endH).padStart(2,'0')}${String(startM).padStart(2,'0')}00`;
            btnGoogle.href = `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dtStart}/${dtEnd}&details=${desc}&location=${loc}`;
        }
    }

    async function submitBooking() {
        const patients = [];
        document.querySelectorAll(".patient-card").forEach((card, idx) => {
            patients.push({
                guest_number: idx + 1,
                guest_label: `Khách ${idx + 1}`,
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
            auto_distribute: window.MSBookingCapacity ? window.MSBookingCapacity.getAutoDistribute() : false,
            patients: patients
        };

        console.log("Sending Payload:", payload);

        let generatedCode = 'MS-GRP-' + new Date().toISOString().slice(0, 10).replace(/-/g, '') + '-' + Math.floor(1000 + Math.random() * 9000);
        let serverData = null;
        try {
            const response = await fetch('/api/bookings/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' },
                body: JSON.stringify(payload)
            });
            serverData = await response.json().catch(() => null);
            if (!response.ok) {
                const errMsg = (serverData && (serverData.error || serverData.warning_message || serverData.message)) || 'Không đủ ghế trống tại khung giờ đã chọn. Vui lòng bật tự động phân phối hoặc chọn giờ khác.';
                alert(errMsg);
                currentStep = 3;
                updateUI();
                if (window.MSBookingCapacity) window.MSBookingCapacity.sync(bookingData);
                return;
            }
            if (serverData) {
                if (serverData.pnr_code) generatedCode = serverData.pnr_code;
                else if (serverData.group_code) generatedCode = serverData.group_code;
                else if (serverData.booking_code) generatedCode = serverData.booking_code;
            }
        } catch (error) {
            console.warn('Backend Django chưa sẵn sàng, dùng mã dự phòng:', error);
        }
        const displayGroupCode = document.getElementById('displayGroupCode');
        if (displayGroupCode) displayGroupCode.innerText = 'Mã đặt chỗ: ' + generatedCode;
        setupCalendarButtons({ groupCode: generatedCode, clinicName: bookingData.clinicName, date: bookingData.date, time: bookingData.time });
        const summaryListEl = document.getElementById('summaryList');
        if (serverData && window.MSBookingCapacity && typeof window.MSBookingCapacity.renderBookingResult === 'function') {
            window.MSBookingCapacity.renderBookingResult(serverData, summaryListEl, displayGroupCode, bookingData, servicesList);
            return;
        }
        let summaryHtml = `<div class="summary-item"><strong>Cơ sở:</strong> ${bookingData.clinicName} | <strong>Ngày:</strong> ${bookingData.date}</div>`;
        patients.forEach((p, idx) => {
            const sName = servicesList.find(s => s.id == p.category_id)?.name || 'Dịch vụ nha khoa';
            summaryHtml += `<div class="summary-item"><strong>Khách ${idx + 1}:</strong> ${p.fullName} - ${p.phone}<br><small>Dịch vụ: ${sName} | Giờ: ${p.start_time}</small></div>`;
        });
        summaryListEl.innerHTML = summaryHtml;
    }
});
</script>
<script src="<?php echo esc_url(get_template_directory_uri()); ?>/js/booking-capacity.js?v=1.0.0" defer></script>

<?php get_footer(); ?>