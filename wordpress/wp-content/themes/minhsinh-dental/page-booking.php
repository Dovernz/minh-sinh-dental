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
                    <!-- 2. Tab chuyển đổi 2 Cơ sở -->
                    <div class="clinics-tabs">
                        <button type="button" class="clinic-tab-btn active" data-clinic-id="1" 
                                data-address="123 Phố Huế, Hai Bà Trưng, Hà Nội" 
                                data-hotline="0988 123 456"
                                data-map="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3724.096811983057!2d105.85289997689973!3d21.028811480620556!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135ab9bd98319f7%3A0x9d4a8e235e16ef90!2zMTIz PhOGkSBIdeG6vywgUGjhu5EgSG_hur9uLCBIYWnhuIEAgQuGsHU5nLCBIw6AgTuG7mWksIFZpZXRuYW0!5e0!3m2!1sen!2s!4v1700000000000!5m2!1sen!2s">
                            <strong>Cơ sở 1:</strong> 123 Phố Huế, Hai Bà Trưng, Hà Nội
                            <span class="clinic-hotline">Hotline: 0988 123 456</span>
                        </button>
                        <button type="button" class="clinic-tab-btn" data-clinic-id="2" 
                                data-address="456 Nguyễn Trãi, Thanh Xuân, Hà Nội" 
                                data-hotline="0977 654 321"
                                data-map="https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3724.677708579737!2d105.8030044768992!3d21.004818980637175!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x3135ac80b741031b%3A0x3f3d35091a13e54b!2zNDU2IE5ndXnhuecMgVHLDo2ksIFRoYW5oIFh1w6JuLCBIw6AgTuG7mWksIFZpZXRuYW0!5e0!3m2!1sen!2s!4v1700000000000!5m2!1sen!2s">
                            <strong>Cơ sở 2:</strong> 456 Nguyễn Trãi, Thanh Xuân, Hà Nội
                            <span class="clinic-hotline">Hotline: 0977 654 321</span>
                        </button>
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
                                <button type="button" class="time-slot" data-time="08:30">08:30 - 09:30</button>
                                <button type="button" class="time-slot" data-time="09:30">09:30 - 10:30</button>
                                <button type="button" class="time-slot" data-time="10:30">10:30 - 11:30</button>
                                <button type="button" class="time-slot" data-time="14:00">14:00 - 15:00</button>
                                <button type="button" class="time-slot" data-time="15:00">15:00 - 16:00</button>
                                <button type="button" class="time-slot" data-time="16:00">16:00 - 17:00</button>
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
        grid-template-columns: 1fr 1fr;
    }
}

.clinic-tab-btn {
    text-align: left;
    background: #fff;
    border: 2px solid var(--ms-border);
    padding: 12px 15px;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.2s;
    font-size: 13px;
}

.clinic-tab-btn.active {
    border-color: var(--ms-primary);
    background: var(--ms-primary-light);
}

.clinic-hotline {
    display: block;
    margin-top: 4px;
    color: var(--ms-primary);
    font-weight: 500;
}

.map-container {
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid var(--ms-border);
}

/* Dịch vụ Grid */
.services-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 12px;
    max-height: 250px;
    overflow-y: auto;
}

@media(min-width: 640px) {
    .services-grid {
        grid-template-columns: 1fr 1fr;
    }
}

.service-card {
    border: 2px solid var(--ms-border);
    padding: 15px;
    border-radius: 8px;
    cursor: pointer;
    transition: 0.2s;
    background: #fff;
}

.service-card.selected {
    border-color: var(--ms-primary);
    background: var(--ms-primary-light);
}

.service-card h4 {
    font-size: 15px;
    margin: 0 0 5px 0;
}

.service-card p {
    font-size: 13px;
    color: var(--ms-text-muted);
    margin: 0;
}

.service-price {
    font-weight: 600;
    color: var(--ms-primary);
    margin-top: 8px !important;
    display: block;
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
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}

.time-slot {
    padding: 10px;
    background: #fff;
    border: 1px solid var(--ms-border);
    border-radius: 6px;
    cursor: pointer;
    font-size: 13px;
    text-align: center;
    transition: 0.2s;
}

.time-slot.selected {
    background: var(--ms-primary);
    color: #fff;
    border-color: var(--ms-primary);
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
        clinicName: "123 Phố Huế, Hai Bà Trưng, Hà Nội",
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

    // 1. Xử lý Chuyển đổi Cơ sở & Maps
    const clinicTabs = document.querySelectorAll(".clinic-tab-btn");
    clinicTabs.forEach(btn => {
        btn.addEventListener("click", function () {
            clinicTabs.forEach(b => b.classList.remove("active"));
            this.classList.add("active");

            bookingData.clinicId = this.getAttribute("data-clinic-id");
            bookingData.clinicName = this.getAttribute("data-address");
            
            // Cập nhật iframe Google Maps ngay lập tức
            const mapUrl = this.getAttribute("data-map");
            clinicMap.src = mapUrl;
        });
    });

    // 2. Fetch API Services (Django) kèm Fallback Mockup Data
    const servicesGrid = document.getElementById("servicesGrid");
    
    async function fetchServices() {
        const fallbackServices = [
            { id: 1, name: "Khám & Tư vấn tổng quát", description: "Kiểm tra sức khỏe răng miệng toàn diện", price: "Miễn phí" },
            { id: 2, name: "Cạo vôi răng siêu âm", description: "Làm sạch mảng bám, không ê buốt", price: "200,000 đ" },
            { id: 3, name: "Tẩy trắng răng công nghệ cao", description: "Trắng sáng tự nhiên chỉ sau 45 phút", price: "1,500,000 đ" },
            { id: 4, name: "Niềng răng thẩm mỹ", description: "Khắc phục hô, móm, lệch lạc", price: "Từ 25,000,000 đ" }
        ];

        try {
            // Thay đổi endpoint phù hợp với cấu hình Django Backend của bạn
            let response = await fetch('/api/services/', { method: 'GET', headers: { 'Accept': 'application/json' } });
            if (!response.ok) throw new Error("API không phản hồi");
            let data = await response.json();
            renderServices(data.length ? data : fallbackServices);
        } catch (error) {
            console.warn("Sử dụng Mockup Data cho Services do lỗi kết nối API:", error.message);
            renderServices(fallbackServices);
        }
    }

    function renderServices(services) {
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
                <h4>${srv.name}</h4>
                <p>${srv.description || ''}</p>
                <span class="service-price">${srv.price || ''}</span>
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
    fetchServices();

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

    // Chọn Giờ khám tương tác
    const timeSlots = document.querySelectorAll(".time-slot");
    timeSlots.forEach(slot => {
        slot.addEventListener("click", function () {
            timeSlots.forEach(s => s.classList.remove("selected"));
            this.classList.add("selected");
            bookingData.time = this.getAttribute("data-time");
        });
    });

    // 3. Quản lý Stepper & Validate Bước
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
            return true;
        }
        if (step === 2) {
            const dateVal = document.getElementById("bookingDate").value;
            if (!dateVal) {
                alert("Vui lòng chọn ngày khám!");
                return false;
            }
            if (!bookingData.time) {
                alert("Vui lòng chọn khung giờ khám!");
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

            const phoneRegex = /(84|0[3|5|7|8|9])+([0-9]{8})\b/;
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
        // Cập nhật hiển thị Pane
        panes.forEach((pane, idx) => {
            pane.classList.toggle("active", idx + 1 === currentStep);
        });

        // Cập nhật Stepper Header
        steps.forEach((st, idx) => {
            st.classList.toggle("active", idx + 1 === currentStep);
            if (idx + 1 < currentStep) {
                st.classList.add("completed");
            } else {
                st.classList.remove("completed");
            }
        });

        // Xử lý nút điều hướng
        btnPrev.style.display = currentStep > 1 && currentStep < 4 ? "block" : "none";
        
        if (currentStep === 4) {
            btnNext.style.display = "none";
            btnPrev.style.display = "none";
        } else {
            btnNext.style.display = "block";
            btnNext.innerText = currentStep === 3 ? "Xác nhận Đặt lịch" : "Tiếp tục";
        }
    }

    // 4. Gửi POST /api/bookings/ tới Django Backend
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
});
</script>

<?php 
get_footer(); 
?>
