<?php 
/* Template Name: Trang Đặt Lịch Hẹn */ 
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
                    <div class="step-name">Chọn Dịch vụ & Cơ sở</div>
                </div>
                <div class="step-item" data-step="2">
                    <div class="step-counter">2</div>
                    <div class="step-name">Thời gian & Bác sĩ</div>
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
                    <!-- 2. Tab chuyển đổi Cơ sở (Tải động từ API Django /api/clinics/) -->
                    <div class="clinics-tabs" id="clinicsTabs">
                        <div class="clinic-loading" style="grid-column: 1/-1; padding: 12px; color: var(--ms-text-muted); font-size: 13.5px;">Đang tải danh sách cơ sở...</div>
                    </div>

                    <!-- Google Maps Iframe -->
                    <div class="map-container">
                        <iframe id="clinicMap" src="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3724.096811983057!2d105.85289997689973!3d21.028811480620556!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135ab9bd98319f7%3A0x9d4a8e235e16ef90!2zMTIz PhOGkSBIdeG6vywgUGjhu5EgSG_hur9uLCBIYWnhuIEAgQuGsHU5nLCBIw6AgTuG7mWksIFZpZXRuYW0!5e0!3m2!1sen!2s!4v1700000000000!5m2!1sen!2s" width="100%" height="200" style="border:0;" allowfullscreen="" loading="lazy"></iframe>
                    </div>

                    <h3 class="pane-title" style="margin-top: 24px;">Chọn Dịch Vụ Nha Khoa</h3>
                    <div class="services-grid" id="servicesGrid">
                        <!-- Render dynamic từ JS hoặc Mockup -->
                        <div class="service-loading">Đang tải danh sách dịch vụ...</div>
                    </div>
                </div>

                <!-- BƯỚC 2: Chọn Thời gian & Bác sĩ -->
                <div class="booking-step-pane" id="paneStep2">
                    <h3 class="pane-title">Chọn Bác Sĩ Điều Trị</h3>
                    <div class="doctors-grid" id="doctorsGrid">
                        <div class="doctor-card selected" data-doctor-id="1">
                            <div class="doc-avatar">🦷</div>
                            <div class="doc-info">
                                <h4>ThS.BS Nguyễn Minh Hải</h4>
                                <p>Chuyên gia Răng Hàm Mặt</p>
                            </div>
                        </div>
                        <div class="doctor-card" data-doctor-id="2">
                            <div class="doc-avatar">👩‍⚕️</div>
                            <div class="doc-info">
                                <h4>BS. Trần Thị Mai</h4>
                                <p>Chuyên gia Niềng Răng - Thẩm mỹ</p>
                            </div>
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
                                <div class="slot-loading" style="grid-column: 1/-1; padding: 12px; text-align: center; color: var(--ms-text-muted); font-size: 13px;">Đang tải danh sách khung giờ...</div>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- BƯỚC 3: Điền Thông tin Khách hàng -->
                <div class="booking-step-pane" id="paneStep3">
                    <h3 class="pane-title">Thông tin liên hệ của Quý khách</h3>
                    <div class="customer-form">
                        <div class="form-group">
                            <label for="cusName">Họ và tên <span class="required">*</span></label>
                            <input type="text" id="cusName" class="form-control" placeholder="Nhập họ và tên của bạn">
                            <span class="error-msg" id="errName">Vui lòng nhập họ tên.</span>
                        </div>
                        <div class="form-group">
                            <label for="cusPhone">Số điện thoại <span class="required">*</span></label>
                            <input type="tel" id="cusPhone" class="form-control" placeholder="Nhập số điện thoại (10 chữ số)">
                            <span class="error-msg" id="errPhone">Số điện thoại không hợp lệ.</span>
                        </div>
                        <div class="form-group">
                            <label for="cusEmail">Email (Không bắt buộc)</label>
                            <input type="email" id="cusEmail" class="form-control" placeholder="example@gmail.com">
                        </div>
                        <div class="form-group">
                            <label for="cusNote">Ghi chú thêm</label>
                            <textarea id="cusNote" class="form-control" rows="3" placeholder="Triệu chứng hoặc yêu cầu đặc biệt..."></textarea>
                        </div>
                    </div>
                </div>

                <!-- BƯỚC 4: Hoàn tất Đặt lịch -->
                <div class="booking-step-pane" id="paneStep4">
                    <div class="success-box" id="successBox">
                        <div class="success-icon">✓</div>
                        <h3>Đặt Lịch Thành Công!</h3>
                        <p>Cảm ơn quý khách đã tin tưởng Nha khoa Minh Sinh. Mã đặt lịch của bạn là:</p>
                        <div class="booking-code-display" id="displayBookingCode">MS-XXXXXX</div>
                        
                        <div class="summary-card">
                            <h4>Tóm tắt lịch hẹn:</h4>
                            <ul id="summaryList">
                                <!-- Dynamic review data -->
                            </ul>
                        </div>
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

<!-- CSS Nhúng Trực Tiếp (Scoped) -->
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

.minhsinh-booking-wrapper {
    background-color: var(--ms-bg);
    padding: 40px 15px;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
    color: var(--ms-text-dark);
}

.minhsinh-container {
    max-width: 800px;
    margin: 0 auto;
}

.booking-header-section {
    text-align: center;
    margin-bottom: 30px;
}

.booking-main-title {
    font-size: 28px;
    font-weight: 700;
    color: var(--ms-primary);
    margin-bottom: 8px;
}

.booking-sub-title {
    font-size: 15px;
    color: var(--ms-text-muted);
}

.minhsinh-booking-container {
    background: #ffffff;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(37, 99, 235, 0.08);
    overflow: hidden;
    border: 1px solid #e2e8f0;
}

/* Stepper */
.stepper-wrapper {
    display: flex;
    justify-content: space-between;
    background: var(--ms-primary-light);
    padding: 20px 30px;
    border-bottom: 1px solid #e2e8f0;
}

.step-item {
    display: flex;
    align-items: center;
    gap: 10px;
    opacity: 0.5;
    transition: 0.3s;
}

.step-item.active {
    opacity: 1;
}

.step-counter {
    width: 32px;
    height: 32px;
    background: #cbd5e1;
    color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 600;
    font-size: 14px;
}

.step-item.active .step-counter,
.step-item.completed .step-counter {
    background: var(--ms-primary);
}

.step-name {
    font-size: 14px;
    font-weight: 600;
    display: none;
}

@media(min-width: 768px) {
    .step-name {
        display: block;
    }
}

/* Body Panes */
.booking-body {
    padding: 30px;
    min-height: 350px;
}

.booking-step-pane {
    display: none;
}

.booking-step-pane.active {
    display: block;
}

.pane-title {
    font-size: 18px;
    font-weight: 600;
    margin-bottom: 15px;
    color: var(--ms-text-dark);
}

/* Cơ sở & Tabs */
.clinics-tabs {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    margin-bottom: 15px;
}

@media(min-width: 640px) {
    .clinics-tabs {
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    }
}

.clinic-tab-btn {
    text-align: left;
    background: #fff;
    border: 2px solid var(--ms-border);
    padding: 14px 16px;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 13.5px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.clinic-tab-btn:hover {
    border-color: var(--ms-primary);
    box-shadow: 0 4px 12px rgba(0, 102, 204, 0.08);
}

.clinic-tab-btn.active {
    border-color: var(--ms-primary);
    background: var(--ms-primary-light);
    box-shadow: 0 4px 12px rgba(0, 102, 204, 0.12);
}

.clinic-tab-btn strong {
    font-size: 14.5px;
    color: var(--ms-text-dark);
}

.clinic-address-text {
    font-size: 13px;
    color: var(--ms-text-muted);
}

.clinic-hotline {
    display: inline-block;
    margin-top: 4px;
    color: var(--ms-primary);
    font-weight: 600;
    font-size: 12.5px;
}

.map-container {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--ms-border);
}

/* Dịch vụ Grid - Giao diện thoáng đãng, không giới hạn chiều cao gò bó */
.services-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 16px;
    margin-bottom: 24px;
}

@media(min-width: 640px) {
    .services-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 16px;
    }
}

@media(min-width: 1024px) {
    .services-grid {
        grid-template-columns: repeat(2, 1fr);
        gap: 18px;
    }
}

.service-card {
    border: 2px solid var(--ms-border);
    padding: 18px 20px;
    border-radius: 12px;
    cursor: pointer;
    transition: all 0.25s ease;
    background: #fff;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    position: relative;
}

.service-card:hover {
    border-color: var(--ms-primary);
    transform: translateY(-2px);
    box-shadow: 0 8px 18px rgba(0, 102, 204, 0.12);
}

.service-card.selected {
    border-color: var(--ms-primary);
    background: var(--ms-primary-light);
    box-shadow: 0 4px 14px rgba(0, 102, 204, 0.16);
}

.service-card h4 {
    font-size: 16px;
    font-weight: 700;
    color: var(--ms-text-dark, #1e293b);
    margin: 0 0 8px 0;
    line-height: 1.4;
}

.service-card p {
    font-size: 13.5px;
    color: var(--ms-text-muted);
    margin: 0 0 12px 0;
    line-height: 1.5;
    flex-grow: 1;
}

.service-price {
    font-weight: 700;
    font-size: 15px;
    color: var(--ms-primary);
    margin-top: auto;
    display: inline-block;
}

/* Bác sĩ & Thời gian */
.doctors-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
}

@media(min-width: 640px) {
    .doctors-grid {
        grid-template-columns: 1fr 1fr;
    }
}

.doctor-card {
    display: flex;
    align-items: center;
    gap: 12px;
    border: 2px solid var(--ms-border);
    padding: 12px;
    border-radius: 8px;
    cursor: pointer;
}

.doctor-card.selected {
    border-color: var(--ms-primary);
    background: var(--ms-primary-light);
}

.doc-avatar {
    font-size: 24px;
    background: #e2e8f0;
    width: 45px;
    height: 45px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
}

.doc-info h4 {
    font-size: 14px;
    margin: 0;
}

.doc-info p {
    font-size: 12px;
    color: var(--ms-text-muted);
    margin: 2px 0 0 0;
}

.datetime-picker-wrapper {
    display: flex;
    flex-direction: column;
    gap: 15px;
}

.time-slots-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
    gap: 12px;
}

.time-slot {
    padding: 12px 10px;
    background: #fff;
    border: 1.5px solid var(--ms-border);
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    text-align: center;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    min-height: 64px;
}

.time-slot:hover:not(:disabled):not(.full) {
    border-color: var(--ms-primary);
    background: #f8fafc;
    transform: translateY(-1px);
}

.time-slot.selected {
    background: var(--ms-primary) !important;
    color: #fff !important;
    border-color: var(--ms-primary) !important;
}

.time-slot.selected .slot-badge {
    background: rgba(255, 255, 255, 0.25) !important;
    color: #fff !important;
}

.time-slot:disabled, .time-slot.full, .time-slot.disabled {
    background: #f1f5f9 !important;
    border-color: #e2e8f0 !important;
    color: #94a3b8 !important;
    cursor: not-allowed !important;
    opacity: 0.75;
    pointer-events: none;
    box-shadow: none !important;
}

.slot-time {
    font-weight: 600;
    font-size: 13px;
    display: block;
}

.slot-badge {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 12px;
    font-weight: 500;
    display: inline-block;
}

.slot-badge.avail-badge {
    background: #e0f2fe;
    color: #0369a1;
}

.slot-badge.full-badge {
    background: #e2e8f0;
    color: #64748b;
}

/* Form controls */
.form-group {
    margin-bottom: 15px;
}

.form-group label {
    display: block;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 6px;
}

.required {
    color: var(--ms-error);
}

.form-control {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid var(--ms-border);
    border-radius: 6px;
    font-size: 14px;
    outline: none;
    transition: 0.2s;
}

.form-control:focus {
    border-color: var(--ms-primary);
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.error-msg {
    color: var(--ms-error);
    font-size: 12px;
    margin-top: 4px;
    display: none;
}

.form-group.has-error .form-control {
    border-color: var(--ms-error);
}

.form-group.has-error .error-msg {
    display: block;
}

/* Success Step */
.success-box {
    text-align: center;
    padding: 20px 0;
}

.success-icon {
    width: 60px;
    height: 60px;
    background: var(--ms-success);
    color: #fff;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    margin: 0 auto 15px auto;
}

.booking-code-display {
    font-size: 22px;
    font-weight: bold;
    color: var(--ms-primary);
    background: var(--ms-primary-light);
    display: inline-block;
    padding: 8px 20px;
    border-radius: 6px;
    margin: 10px 0 20px 0;
    letter-spacing: 1px;
}

.summary-card {
    text-align: left;
    background: #f8fafc;
    border: 1px solid var(--ms-border);
    padding: 15px;
    border-radius: 8px;
    max-width: 450px;
    margin: 0 auto;
}

.summary-card h4 {
    margin: 0 0 10px 0;
    font-size: 14px;
}

.summary-card ul {
    margin: 0;
    padding-left: 20px;
    font-size: 13px;
    color: var(--ms-text-muted);
}

.summary-card li {
    margin-bottom: 5px;
}

/* Footer Actions */
.booking-footer-actions {
    display: flex;
    justify-content: space-between;
    padding: 20px 30px;
    background: #f8fafc;
    border-top: 1px solid #e2e8f0;
}

.btn-ms {
    padding: 10px 24px;
    border-radius: 6px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: 0.2s;
    border: none;
}

.btn-secondary {
    background: #e2e8f0;
    color: var(--ms-text-dark);
}

.btn-secondary:hover {
    background: #cbd5e1;
}

.btn-primary {
    background: var(--ms-primary);
    color: #fff;
}

.btn-primary:hover {
    background: var(--ms-primary-dark);
}
</style>

<!-- JS Thuần Độc Lập (Vanilla JS) -->
<script>
document.addEventListener("DOMContentLoaded", function () {
    // State lưu trữ dữ liệu booking
    const bookingData = {
        clinicId: "1",
        clinicName: "Cơ sở 1 - 123 Phố Huế, Hai Bà Trưng, Hà Nội",
        serviceId: null,
        serviceName: null,
        doctorId: "1",
        doctorName: "ThS.BS Nguyễn Minh Hải",
        date: "",
        time: "",
        customerName: "",
        customerPhone: "",
        customerEmail: "",
        customerNote: ""
    };

    let currentStep = 1;
    const totalSteps = 4;

    // DOM Elements
    const panes = document.querySelectorAll(".booking-step-pane");
    const steps = document.querySelectorAll(".step-item");
    const btnPrev = document.getElementById("btnPrev");
    const btnNext = document.getElementById("btnNext");
    const clinicMap = document.getElementById("clinicMap");
    const clinicsTabsContainer = document.getElementById("clinicsTabs");
    const timeSlotsGrid = document.getElementById("timeSlotsGrid");
    const bookingDateInput = document.getElementById("bookingDate");

    // Khởi tạo Ngày khám mặc định (Hôm nay) & giới hạn ngày quá khứ
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    const todayStr = `${yyyy}-${mm}-${dd}`;

    if (bookingDateInput) {
        bookingDateInput.min = todayStr;
        bookingDateInput.value = todayStr;
        bookingData.date = todayStr;

        bookingDateInput.addEventListener("change", function () {
            bookingData.date = this.value;
            bookingData.time = ""; // Reset slot khi đổi ngày
            fetchAvailableSlots();
        });
    }

    // 1. Fetch Cơ sở Động từ Django Backend (/api/clinics/)
    const fallbackClinics = [
        {
            clinic_id: 1,
            name: "Cơ sở 1: Phố Huế",
            address: "123 Phố Huế, Hai Bà Trưng, Hà Nội",
            hotline: "0988 123 456",
            map_url: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3724.096811983057!2d105.85289997689973!3d21.028811480620556!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135ab9bd98319f7%3A0x9d4a8e235e16ef90!2zMTIz PhOGkSBIdeG6vywgUGjhu5EgSG_hur9uLCBIYWnhuIEAgQuGsHU5nLCBIw6AgTuG7mWksIFZpZXRuYW0!5e0!3m2!1sen!2s!4v1700000000000!5m2!1sen!2s"
        },
        {
            clinic_id: 2,
            name: "Cơ sở 2: Nguyễn Trãi",
            address: "456 Nguyễn Trãi, Thanh Xuân, Hà Nội",
            hotline: "0977 654 321",
            map_url: "https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3724.677708579737!2d105.8030044768992!3d21.004818980637175!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135ac80b741031b%3A0x3f3d35091a13e54b!2zNDU2IE5ndXnhuecMgVHLDo2ksIFRoYW5oIFh1w6JuLCBIw6AgTuG7mWksIFZpZXRuYW0!5e0!3m2!1sen!2s!4v1700000000000!5m2!1sen!2s"
        }
    ];

    async function fetchClinics() {
        try {
            const response = await fetch('/api/clinics/', {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            if (!response.ok) throw new Error("API clinics không phản hồi");
            const data = await response.json();
            const clinics = Array.isArray(data) ? data : (data.clinics || fallbackClinics);
            renderClinics(clinics.length ? clinics : fallbackClinics);
        } catch (error) {
            console.warn("Dùng fallback clinics do lỗi kết nối API:", error.message);
            renderClinics(fallbackClinics);
        }
    }

    function renderClinics(clinics) {
        if (!clinicsTabsContainer) return;
        clinicsTabsContainer.innerHTML = "";

        clinics.forEach((clinic, index) => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.className = `clinic-tab-btn ${index === 0 ? 'active' : ''}`;
            const cId = String(clinic.clinic_id || clinic.id);
            const cName = clinic.name || `Cơ sở ${cId}`;
            const cAddr = clinic.address || '';
            const cHotline = clinic.hotline || '1900 6868';
            const cMap = clinic.map_url || (fallbackClinics[index] ? fallbackClinics[index].map_url : fallbackClinics[0].map_url);

            btn.setAttribute("data-clinic-id", cId);
            btn.setAttribute("data-clinic-name", cName);
            btn.setAttribute("data-address", cAddr);
            btn.setAttribute("data-hotline", cHotline);
            btn.setAttribute("data-map", cMap);

            btn.innerHTML = `
                <strong>${cName}</strong>
                <span class="clinic-address-text">${cAddr}</span>
                <span class="clinic-hotline">Hotline: ${cHotline}</span>
            `;

            if (index === 0) {
                bookingData.clinicId = cId;
                bookingData.clinicName = `${cName} - ${cAddr}`;
                if (clinicMap && cMap) {
                    clinicMap.src = cMap;
                }
            }

            btn.addEventListener("click", function () {
                document.querySelectorAll(".clinic-tab-btn").forEach(b => b.classList.remove("active"));
                this.classList.add("active");

                bookingData.clinicId = this.getAttribute("data-clinic-id");
                bookingData.clinicName = `${this.getAttribute("data-clinic-name")} - ${this.getAttribute("data-address")}`;

                // Cập nhật iframe Google Maps
                const mapUrl = this.getAttribute("data-map");
                if (clinicMap && mapUrl) {
                    clinicMap.src = mapUrl;
                }

                // Tự động tải lại slot khi chuyển cơ sở
                bookingData.time = "";
                fetchAvailableSlots();
            });

            clinicsTabsContainer.appendChild(btn);
        });

        // Tải slots lần đầu sau khi có clinicId
        fetchAvailableSlots();
    }

    // 2. Fetch API Services (Django) kèm Fallback Mockup Data
    const servicesGrid = document.getElementById("servicesGrid");

    async function fetchServices() {
        const fallbackServices = [
            { id: 1, name: "Khám & Tư vấn tổng quát", description: "Kiểm tra sức khỏe răng miệng toàn diện cùng chuyên gia", price: "Miễn phí" },
            { id: 2, name: "Cạo vôi răng siêu âm", description: "Làm sạch mảng bám, đánh bóng men răng, êm ái không ê buốt", price: "200,000 đ" },
            { id: 3, name: "Tẩy trắng răng công nghệ cao", description: "Bật 2-3 tông sáng tự nhiên chỉ sau 45 phút điều trị", price: "1,500,000 đ" },
            { id: 4, name: "Niềng răng thẩm mỹ", description: "Mắc cài kim loại/pha lê cao cấp, khắc phục hô, móm, khấp khểnh", price: "Từ 25,000,000 đ" }
        ];

        try {
            let response = await fetch('/api/services/', { method: 'GET', headers: { 'Accept': 'application/json' } });
            if (!response.ok) throw new Error("API services không phản hồi");
            let data = await response.json();
            renderServices(data.length ? data : fallbackServices);
        } catch (error) {
            console.warn("Sử dụng Mockup Data cho Services do lỗi kết nối API:", error.message);
            renderServices(fallbackServices);
        }
    }

    function renderServices(services) {
        if (!servicesGrid) return;
        servicesGrid.innerHTML = "";
        services.forEach((srv, index) => {
            const card = document.createElement("div");
            card.className = `service-card ${index === 0 ? 'selected' : ''}`;
            if (index === 0) {
                bookingData.serviceId = srv.id;
                bookingData.serviceName = srv.name;
            }
            card.setAttribute("data-service-id", srv.id);
            card.setAttribute("data-service-name", srv.name);
            card.innerHTML = `
                <div>
                    <h4>${srv.name}</h4>
                    <p>${srv.description || 'Dịch vụ chăm sóc nha khoa chuẩn y khoa tại Nha Khoa Minh Sinh.'}</p>
                </div>
                <span class="service-price">${srv.price || 'Liên hệ tư vấn'}</span>
            `;

            card.addEventListener("click", function () {
                document.querySelectorAll(".service-card").forEach(c => c.classList.remove("selected"));
                this.classList.add("selected");
                bookingData.serviceId = this.getAttribute("data-service-id");
                bookingData.serviceName = this.getAttribute("data-service-name");
            });

            servicesGrid.appendChild(card);
        });
    }

    // 3. Quản lý Khung giờ & Capacity Động (/api/available-slots/)
    const fallbackSlots = [
        { time: "08:30 - 09:30", start_time: "08:30", available_chairs: 3, total_chairs: 4, is_full: false },
        { time: "09:30 - 10:30", start_time: "09:30", available_chairs: 2, total_chairs: 4, is_full: false },
        { time: "10:30 - 11:30", start_time: "10:30", available_chairs: 0, total_chairs: 4, is_full: true },
        { time: "14:00 - 15:00", start_time: "14:00", available_chairs: 4, total_chairs: 4, is_full: false },
        { time: "15:00 - 16:00", start_time: "15:00", available_chairs: 1, total_chairs: 4, is_full: false },
        { time: "16:00 - 17:00", start_time: "16:00", available_chairs: 0, total_chairs: 4, is_full: true }
    ];

    async function fetchAvailableSlots() {
        if (!timeSlotsGrid) return;
        const clinicId = bookingData.clinicId;
        const dateVal = bookingData.date || (bookingDateInput ? bookingDateInput.value : '');

        if (!clinicId || !dateVal) {
            timeSlotsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--ms-text-muted); padding: 15px;">Vui lòng chọn ngày khám để xem khung giờ.</div>`;
            return;
        }

        timeSlotsGrid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; color: var(--ms-text-muted); padding: 15px;">Đang kiểm tra chỗ trống...</div>`;

        try {
            const response = await fetch(`/api/available-slots/?clinic_id=${clinicId}&date=${dateVal}`, {
                method: 'GET',
                headers: { 'Accept': 'application/json' }
            });
            if (!response.ok) throw new Error("API available-slots không phản hồi");
            const data = await response.json();
            renderTimeSlots(Array.isArray(data) && data.length ? data : fallbackSlots);
        } catch (error) {
            console.warn("Dùng fallback slots do lỗi API:", error.message);
            renderTimeSlots(fallbackSlots);
        }
    }

    function renderTimeSlots(slots) {
        if (!timeSlotsGrid) return;
        timeSlotsGrid.innerHTML = "";

        let hasSelected = false;

        slots.forEach(slot => {
            const btn = document.createElement("button");
            btn.type = "button";
            const timeLabel = slot.time || slot.start_time;
            const slotVal = slot.start_time || slot.time;
            const isFull = slot.is_full === true || slot.available_chairs <= 0;

            if (isFull) {
                btn.className = "time-slot full disabled";
                btn.disabled = true;
                btn.innerHTML = `
                    <span class="slot-time">${timeLabel}</span>
                    <span class="slot-badge full-badge">Đã kín</span>
                `;
            } else {
                const isCurrent = bookingData.time === slotVal;
                if (isCurrent) hasSelected = true;

                btn.className = `time-slot ${isCurrent ? 'selected' : ''}`;
                btn.setAttribute("data-time", slotVal);
                btn.innerHTML = `
                    <span class="slot-time">${timeLabel}</span>
                    <span class="slot-badge avail-badge">Còn ${slot.available_chairs} chỗ</span>
                `;

                btn.addEventListener("click", function () {
                    document.querySelectorAll(".time-slot").forEach(s => s.classList.remove("selected"));
                    this.classList.add("selected");
                    bookingData.time = slotVal;
                });
            }

            timeSlotsGrid.appendChild(btn);
        });

        // Nếu slot đã chọn trước đó giờ đã kín hoặc không tồn tại, reset
        if (!hasSelected && bookingData.time) {
            bookingData.time = "";
        }
    }

    // Chọn Bác sĩ tương tác
    const doctorCards = document.querySelectorAll(".doctor-card");
    doctorCards.forEach(doc => {
        doc.addEventListener("click", function () {
            doctorCards.forEach(d => d.classList.remove("selected"));
            this.classList.add("selected");
            bookingData.doctorId = this.getAttribute("data-doctor-id");
            bookingData.doctorName = this.querySelector("h4").innerText;
        });
    });

    // 4. Quản lý Stepper & Validate Bước
    btnNext.addEventListener("click", function () {
        if (validateStep(currentStep)) {
            if (currentStep < totalSteps) {
                currentStep++;
                updateWizard();
            }
        }
    });

    btnPrev.addEventListener("click", function () {
        if (currentStep > 1) {
            currentStep--;
            updateWizard();
        }
    });

    function validateStep(step) {
        if (step === 1) {
            if (!bookingData.serviceId) {
                alert("Vui lòng chọn một dịch vụ nha khoa!");
                return false;
            }
            if (!bookingData.clinicId) {
                alert("Vui lòng chọn cơ sở nha khoa!");
                return false;
            }
            return true;
        }
        if (step === 2) {
            const dateVal = document.getElementById("bookingDate").value;
            if (!dateVal) {
                alert("Vui lòng chọn ngày khám!");
                return false;
            }
            if (!bookingData.time) {
                alert("Vui lòng chọn khung giờ khám còn chỗ trống!");
                return false;
            }
            bookingData.date = dateVal;
            return true;
        }
        if (step === 3) {
            let isValid = true;
            const nameInput = document.getElementById("cusName");
            const phoneInput = document.getElementById("cusPhone");

            const nameGroup = nameInput.closest(".form-group");
            const phoneGroup = phoneInput.closest(".form-group");

            nameGroup.classList.remove("has-error");
            phoneGroup.classList.remove("has-error");

            if (!nameInput.value.trim()) {
                nameGroup.classList.add("has-error");
                isValid = false;
            }

            const phoneRegex = /(84|0[3|5|7|8|9])+([0-9]{8})/;
            if (!phoneRegex.test(phoneInput.value.trim())) {
                phoneGroup.classList.add("has-error");
                isValid = false;
            }

            if (isValid) {
                bookingData.customerName = nameInput.value.trim();
                bookingData.customerPhone = phoneInput.value.trim();
                bookingData.customerEmail = document.getElementById("cusEmail").value.trim();
                bookingData.customerNote = document.getElementById("cusNote").value.trim();

                // Tiến hành Gửi POST API Django ở bước 4
                submitBookingToBackend();
            }
            return isValid;
        }
        return true;
    }

    function updateWizard() {
        panes.forEach((pane, idx) => {
            pane.classList.toggle("active", idx + 1 === currentStep);
        });

        steps.forEach((st, idx) => {
            st.classList.toggle("active", idx + 1 === currentStep);
            if (idx + 1 < currentStep) {
                st.classList.add("completed");
            } else {
                st.classList.remove("completed");
            }
        });

        btnPrev.style.display = currentStep > 1 && currentStep < 4 ? "block" : "none";

        if (currentStep === 4) {
            btnNext.style.display = "none";
            btnPrev.style.display = "none";
        } else {
            btnNext.style.display = "block";
            btnNext.innerText = currentStep === 3 ? "Xác nhận Đặt lịch" : "Tiếp tục";
        }
    }

    // 5. Gửi POST /api/bookings/ tới Django Backend
    async function submitBookingToBackend() {
        const payload = {
            clinic_id: bookingData.clinicId,
            service_id: bookingData.serviceId,
            doctor_id: bookingData.doctorId,
            booking_date: bookingData.date,
            booking_time: bookingData.time,
            customer_name: bookingData.customerName,
            customer_phone: bookingData.customerPhone,
            customer_email: bookingData.customerEmail,
            customer_note: bookingData.customerNote
        };

        let generatedCode = "MS-" + Math.floor(100000 + Math.random() * 900000);

        try {
            let response = await fetch('/api/bookings/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (response.ok) {
                let resData = await response.json();
                if (resData.booking_code) {
                    generatedCode = resData.booking_code;
                }
            }
        } catch (error) {
            console.warn("Backend Django chưa sẵn sàng, dùng mã giả lập:", error);
        }

        // Hiển thị kết quả hoàn tất
        document.getElementById("displayBookingCode").innerText = generatedCode;
        document.getElementById("summaryList").innerHTML = `
            <li><strong>Khách hàng:</strong> ${bookingData.customerName} (${bookingData.customerPhone})</li>
            <li><strong>Dịch vụ:</strong> ${bookingData.serviceName}</li>
            <li><strong>Cơ sở:</strong> ${bookingData.clinicName}</li>
            <li><strong>Bác sĩ:</strong> ${bookingData.doctorName}</li>
            <li><strong>Thời gian:</strong> ${bookingData.time} - Ngày ${bookingData.date}</li>
        `;
    }

    // Khởi chạy nạp dữ liệu ban đầu
    fetchClinics();
    fetchServices();
});
</script>

<?php 
get_footer(); 
?>
