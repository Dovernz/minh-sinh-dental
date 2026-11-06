<footer class="site-footer">
    <div class="container">
        <div class="footer-grid">
            <!-- Cột 1: Thông tin phòng khám -->
            <div class="footer-col">
                <div class="logo-wrapper" style="margin-bottom: 16px;">
                    <img src="<?php echo get_template_directory_uri(); ?>/images/logo.png" alt="Logo" class="logo-img">
                    <span class="brand-name">Nha Khoa Minh Sinh</span>
                </div>
                <p style="color: #64748b; font-size: 14px; line-height: 1.7;">
                    Nha khoa Minh Sinh - Tiên phong trong lĩnh vực chăm sóc sức khỏe và thẩm mỹ răng miệng từ năm 1937. Chúng tôi cam kết mang lại nụ cười hoàn hảo và sự tự tin cho mọi khách hàng.
                </p>
                <div style="margin-top: 16px;">
                    <strong style="color: #1e3a8a;">Hotline:</strong> <span style="color: #2563eb; font-weight: 700;">1900 1234 - 0987 654 321</span>
                </div>
            </div>

            <!-- Cột 2: Hệ thống cơ sở khám -->
            <div class="footer-col">
                <h4>Hệ thống cơ sở</h4>
                <ul style="list-style: none; padding: 0; margin: 0; color: #64748b; font-size: 14px; line-height: 2;">
                    <li>📍 <strong>Cơ sở 1:</strong> 123 Phố Huế, Hai Bà Trưng, Hà Nội</li>
                    <li>📍 <strong>Cơ sở 2:</strong> 456 Nguyễn Trãi, Thanh Xuân, Hà Nội</li>
                </ul>
            </div>

            <!-- Cột 3: Giờ làm việc & Đặt hẹn -->
            <div class="footer-col">
                <h4>Thời gian làm việc</h4>
                <p style="color: #64748b; font-size: 14px; line-height: 1.8;">
                    <strong>Thứ 2 - Thứ 7:</strong> 08:00 - 20:00<br>
                    <strong>Chủ nhật:</strong> 08:00 - 17:30<br>
                    <small><i>(Phục vụ cả ngày nghỉ lễ và ngoài giờ theo lịch hẹn)</i></small>
                </p>
                <div style="margin-top: 20px;">
                    <?php $booking_url = get_theme_mod('minhsinh_booking_url', 'http://localhost:8000/booking/'); ?>
                    <a href="<?php echo esc_url($booking_url); ?>" class="btn-booking" style="font-size: 14px; padding: 8px 18px;">
                        Đặt lịch online 24/7
                    </a>
                </div>
            </div>
        </div>

        <div class="footer-bottom">
            &copy; <?php echo date('Y'); ?> Nha Khoa Minh Sinh. Bản quyền thuộc về Nha Khoa Minh Sinh. Giấy phép hoạt động số 1234/BYT-GPHĐ.
        </div>
    </div>
</footer>

<?php wp_footer(); ?>
</body>
</html>
