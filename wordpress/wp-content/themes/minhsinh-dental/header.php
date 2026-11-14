<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
<?php wp_body_open(); ?>

<header class="site-header">
    <div class="container header-inner">
        <!-- Logo -->
        <a href="<?php echo esc_url(home_url('/')); ?>" class="logo-wrapper">
            <?php if (has_custom_logo()) : ?>
                <?php the_custom_logo(); ?>
            <?php else : ?>
                <img src="<?php echo get_template_directory_uri(); ?>/images/logo.png" alt="Nha Khoa Minh Sinh" class="logo-img" onerror="this.src='/static/img/logo.jpg'">
            <?php endif; ?>
            <span class="brand-name">Nha Khoa Minh Sinh</span>
        </a>

        <!-- Menu Navigation -->
        <nav class="main-nav">
            <?php
            wp_nav_menu(array(
                'theme_location' => 'primary-menu',
                'container'      => false,
                'fallback_cb'    => function() {
                    echo '<ul>
                        <li><a href="' . esc_url(home_url('/')) . '">Trang chủ</a></li>
                        <li><a href="' . esc_url(home_url('/dich-vu')) . '">Dịch vụ nha khoa</a></li>
                        <li><a href="' . esc_url(home_url('/bang-gia')) . '">Bảng giá</a></li>
                        <li><a href="' . esc_url(home_url('/bac-si')) . '">Đội ngũ bác sĩ</a></li>
                        <li><a href="' . esc_url(home_url('/tin-tuc')) . '">Tin tức & Tư vấn</a></li>
                    </ul>';
                }
            ));
            ?>
        </nav>

        <!-- Nút Đặt lịch Header (CTA forward sang hệ thống đặt lịch) -->
        <div class="header-action">
            <?php 
                $booking_url = get_theme_mod('minhsinh_booking_url', '/booking/'); 
            ?>
            <a href="<?php echo esc_url($booking_url); ?>" class="btn-booking">
                <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                Đặt lịch ngay
            </a>
        </div>
    </div>
</header>
