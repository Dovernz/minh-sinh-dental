<?php
/**
 * Template Name: Front Page (Landing Page)
 */
get_header();
$booking_url = get_theme_mod('minhsinh_booking_url', 'http://localhost:8000/booking/');
?>

<!-- Hero Banner Section -->
<section class="hero-section">
    <div class="container">
        <h1 class="hero-title">Chào mừng đến với Nha Khoa Minh Sinh</h1>
        <p class="hero-subtitle">
            Hệ thống phòng khám nha khoa tiêu chuẩn quốc tế từ năm 1937. Đội ngũ bác sĩ chuyên môn cao, trang thiết bị chẩn đoán 3D hiện đại, tận tâm vì nụ cười rạng rỡ của bạn.
        </p>
        <div style="display: flex; justify-content: center; gap: 16px; flex-wrap: wrap;">
            <a href="<?php echo esc_url($booking_url); ?>" class="btn-booking" style="font-size: 17px; padding: 14px 32px;">
                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                Đặt lịch khám ngay
            </a>
            <a href="#dich-vu" class="btn-booking" style="background: #fff; color: #1e3a8a !important; border: 1px solid #bfdbfe; font-size: 17px; padding: 14px 28px;">
                Xem các dịch vụ
            </a>
        </div>
    </div>
</section>

<!-- Dịch vụ Nha Khoa Nổi Bật -->
<section id="dich-vu" style="padding: 70px 0;">
    <div class="container">
        <h2 class="section-title">Dịch Vụ Nha Khoa Tiêu Biểu</h2>
        <div class="services-grid">
            <div class="service-card">
                <h3>Niềng răng - Chỉnh nha</h3>
                <p style="color: #64748b; font-size: 15px;">Công nghệ mắc cài thông minh & khay niềng trong suốt Invisalign, phác đồ chuẩn xác giúp khớp cắn chuẩn và khuôn mặt cân đối.</p>
                <a href="<?php echo esc_url($booking_url . '?service=nieng-rang'); ?>" class="btn-booking" style="font-size: 14px; padding: 8px 16px; margin-top: 10px;">Đặt hẹn dịch vụ</a>
            </div>

            <div class="service-card">
                <h3>Trồng răng Implant</h3>
                <p style="color: #64748b; font-size: 15px;">Phục hồi răng đã mất hoàn hảo với trụ Implant nhập khẩu Thụy Sĩ, Mỹ. Ăn nhai bền chắc trọn đời, bảo tồn xương hàm tối đa.</p>
                <a href="<?php echo esc_url($booking_url . '?service=implant'); ?>" class="btn-booking" style="font-size: 14px; padding: 8px 16px; margin-top: 10px;">Đặt hẹn dịch vụ</a>
            </div>

            <div class="service-card">
                <h3>Răng sứ thẩm mỹ</h3>
                <p style="color: #64748b; font-size: 15px;">Dán sứ Veneer, bọc sứ chính hãng bảo hành dài lâu. Màu sắc tự nhiên, dáng răng phong thủy, hạn chế tối đa mài nhỏ răng thật.</p>
                <a href="<?php echo esc_url($booking_url . '?service=rang-su'); ?>" class="btn-booking" style="font-size: 14px; padding: 8px 16px; margin-top: 10px;">Đặt hẹn dịch vụ</a>
            </div>

            <div class="service-card">
                <h3>Nhổ răng khôn không đau</h3>
                <p style="color: #64748b; font-size: 15px;">Ứng dụng sóng siêu âm Piezotome giúp nhổ răng êm ái, bóc tách mô nhẹ nhàng, hồi phục nhanh gấp 3 lần phương pháp truyền thống.</p>
                <a href="<?php echo esc_url($booking_url . '?service=nho-rang'); ?>" class="btn-booking" style="font-size: 14px; padding: 8px 16px; margin-top: 10px;">Đặt hẹn dịch vụ</a>
            </div>
        </div>
    </div>
</section>

<!-- Bài viết & Tư vấn Nha khoa Mới nhất -->
<section style="background-color: #f8fafc; padding: 70px 0;">
    <div class="container">
        <h2 class="section-title">Kiến Thức & Tư Vấn Chuyên Sâu</h2>
        <div class="services-grid">
            <?php
            $recent_posts = new WP_Query(array(
                'posts_per_page' => 6,
                'post_status'    => 'publish'
            ));

            if ($recent_posts->have_posts()) :
                while ($recent_posts->have_posts()) : $recent_posts->the_post(); ?>
                    <div class="service-card">
                        <?php if (has_post_thumbnail()) : ?>
                            <div style="margin-bottom: 14px; border-radius: 8px; overflow: hidden; max-height: 180px;">
                                <?php the_post_thumbnail('medium', array('style' => 'width:100%; height:auto; object-fit:cover;')); ?>
                            </div>
                        <?php endif; ?>
                        <h3 style="font-size: 18px;"><a href="<?php the_permalink(); ?>" style="text-decoration: none; color: #1e3a8a;"><?php the_title(); ?></a></h3>
                        <p style="color: #64748b; font-size: 14px;"><?php echo wp_trim_words(get_the_excerpt(), 18); ?></p>
                        <a href="<?php the_permalink(); ?>" style="color: #2563eb; font-weight: 600; text-decoration: none; font-size: 14px;">Đọc tiếp &rarr;</a>
                    </div>
                <?php endwhile;
                wp_reset_postdata();
            else : ?>
                <div style="grid-column: 1 / -1; text-align: center; color: #64748b; padding: 20px;">
                    Chưa có bài viết nào được đăng. Bạn có thể dễ dàng viết bài mới trong trang Quản trị WordPress!
                </div>
            <?php endif; ?>
        </div>
    </div>
</section>

<!-- Banner Kêu gọi Đặt lịch Cuối Trang -->
<section style="background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); color: #fff; padding: 60px 0; text-align: center;">
    <div class="container">
        <h2 style="font-size: 32px; font-weight: 800; margin-bottom: 16px;">Bạn cần tư vấn tình trạng răng miệng?</h2>
        <p style="font-size: 17px; color: #bfdbfe; max-width: 600px; margin: 0 auto 30px auto;">
            Đặt lịch khám trực tuyến ngay hôm nay để được thăm khám trực tiếp cùng đội ngũ chuyên gia và miễn phí chụp phim X-quang toàn hàm.
        </p>
        <a href="<?php echo esc_url($booking_url); ?>" class="btn-booking" style="background: #fff; color: #1e3a8a !important; font-size: 16px; padding: 14px 36px;">
            Đặt lịch hẹn ngay
        </a>
    </div>
</section>

<?php get_footer(); ?>
