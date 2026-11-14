<?php
/**
 * Template for displaying all single posts
 */
get_header();
$booking_url = get_theme_mod('minhsinh_booking_url', '/booking/');
?>

<main class="container">
    <?php while (have_posts()) : the_post(); ?>
        <article class="article-container">
            <header class="article-header">
                <h1 class="article-title"><?php the_title(); ?></h1>
                <div class="article-meta">
                    <span>Đăng ngày: <?php echo get_the_date('d/m/Y'); ?></span> | 
                    <span>Chuyên mục: <?php the_category(', '); ?></span> | 
                    <span>Tác giả: <?php the_author(); ?></span>
                </div>
            </header>

            <?php if (has_post_thumbnail()) : ?>
                <div style="margin-bottom: 30px; border-radius: 12px; overflow: hidden;">
                    <?php the_post_thumbnail('large', array('style' => 'width:100%; height:auto;')); ?>
                </div>
            <?php endif; ?>

            <div class="article-body">
                <?php the_content(); ?>
            </div>

            <!-- Box Kêu gọi hành động Đặt lịch hẹn sau bài viết -->
            <div class="article-cta-box">
                <h3 style="color: #1e3a8a; font-size: 22px; margin-top: 0; margin-bottom: 10px;">
                    Cần giải đáp chi tiết về dịch vụ này?
                </h3>
                <p style="color: #4b5563; font-size: 15px; margin-bottom: 20px;">
                    Đặt lịch khám ngay để được bác sĩ chuyên khoa thăm khám 1:1 và lập phác đồ điều trị phù hợp nhất với bạn.
                </p>
                <a href="<?php echo esc_url($booking_url); ?>" class="btn-booking" style="font-size: 16px; padding: 12px 30px;">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                    Đặt lịch khám tư vấn ngay
                </a>
            </div>

            <nav style="display: flex; justify-content: space-between; margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb;">
                <div><?php previous_post_link('&larr; %link'); ?></div>
                <div><?php next_post_link('%link &rarr;'); ?></div>
            </nav>
        </article>
    <?php endwhile; ?>
</main>

<?php get_footer(); ?>
