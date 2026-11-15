<?php
/**
 * Main Template File (Fallback)
 */
// Safeguard: Nếu URL là booking hoặc dat-lich, phục vụ thẳng template page-booking.php
$request_uri = $_SERVER['REQUEST_URI'] ?? '';
$path = trim((string)parse_url($request_uri, PHP_URL_PATH), '/');
if ($path === 'booking' || strpos($path, 'booking/') === 0 || $path === 'dat-lich' || strpos($path, 'dat-lich/') === 0) {
    status_header(200);
    include get_template_directory() . '/page-booking.php';
    exit;
}

get_header();
?>

<main class="container" style="padding: 50px 20px;">
    <h1 class="section-title"><?php single_post_title(); ?></h1>
    
    <div class="services-grid">
        <?php if (have_posts()) : while (have_posts()) : the_post(); ?>
            <div class="service-card">
                <?php if (has_post_thumbnail()) : ?>
                    <div style="margin-bottom: 14px; border-radius: 8px; overflow: hidden; max-height: 180px;">
                        <?php the_post_thumbnail('medium', array('style' => 'width:100%; height:auto; object-fit:cover;')); ?>
                    </div>
                <?php endif; ?>
                <h3 style="font-size: 18px;"><a href="<?php the_permalink(); ?>" style="text-decoration: none; color: #1e3a8a;"><?php the_title(); ?></a></h3>
                <p style="color: #64748b; font-size: 14px;"><?php echo wp_trim_words(get_the_excerpt(), 20); ?></p>
                <a href="<?php the_permalink(); ?>" style="color: #2563eb; font-weight: 600; text-decoration: none; font-size: 14px;">Đọc bài viết &rarr;</a>
            </div>
        <?php endwhile; else : ?>
            <p style="text-align: center; color: #64748b;">Không có nội dung nào.</p>
        <?php endif; ?>
    </div>
</main>

<?php get_footer(); ?>
