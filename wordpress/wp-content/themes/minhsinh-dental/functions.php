<?php
// Nhận diện HTTPS reverse proxy (Cloudflare / Nginx SSL termination)
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}

// Triệt tiêu lỗi mixed content HTTP do wp-emoji gây ra
remove_action('wp_head', 'print_emoji_detection_script', 7);
remove_action('wp_print_styles', 'print_emoji_styles');
remove_action('admin_print_scripts', 'print_emoji_detection_script');
remove_action('admin_print_styles', 'print_emoji_styles');
/**
 * Functions and definitions for Minh Sinh Dental Theme
 */

// Đăng ký tính năng của theme
function minhsinh_theme_setup() {
    add_theme_support('title-tag');
    add_theme_support('post-thumbnails');
    add_theme_support('custom-logo');
    
    // Đăng ký vị trí Menu
    register_nav_menus(array(
        'primary-menu' => __('Menu Chính (Header)', 'minhsinh-dental'),
        'footer-menu'  => __('Menu Chân Trang (Footer)', 'minhsinh-dental'),
    ));
}
add_action('after_setup_theme', 'minhsinh_theme_setup');

// Nạp Stylesheet & Script
function minhsinh_enqueue_scripts() {
    wp_enqueue_style('minhsinh-style', get_stylesheet_uri(), array(), '1.0.2');
    wp_enqueue_script('minhsinh-mobile-drawer', get_template_directory_uri() . '/js/mobile-drawer.js', array(), '1.0.0', true);
}
add_action('wp_enqueue_scripts', 'minhsinh_enqueue_scripts');

// Shortcode tạo nút Đặt lịch thông minh kèm dịch vụ
// Cách dùng trong bài viết WordPress: [btn_dat_lich dich_vu="nieng-rang" text="Đặt lịch tư vấn Niềng Răng"]
function minhsinh_booking_btn_shortcode($atts) {
    $a = shortcode_atts(array(
        'dich_vu' => '',
        'text' => 'Đặt lịch khám ngay',
    ), $atts);

    // Đường dẫn trỏ tới cổng hoặc subdomain đặt lịch
    $booking_base_url = get_theme_mod('minhsinh_booking_url', '/booking/');
    $target_url = $booking_base_url;
    if (!empty($a['dich_vu'])) {
        $target_url .= '?service=' . urlencode($a['dich_vu']);
    }

    return sprintf(
        '<div style="text-align:center; margin: 24px 0;">
            <a href="%s" class="btn-booking" target="_blank">
                <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                %s
            </a>
        </div>',
        esc_url($target_url),
        esc_html($a['text'])
    );
}
add_shortcode('btn_dat_lich', 'minhsinh_booking_btn_shortcode');

// Cấu hình URL hệ thống Đặt lịch trong Customizer (Admin WordPress có thể sửa link sau này)
function minhsinh_customize_register($wp_customize) {
    $wp_customize->add_section('minhsinh_system_section', array(
        'title'    => __('Cấu hình Hệ thống Đặt lịch', 'minhsinh-dental'),
        'priority' => 30,
    ));

    $wp_customize->add_setting('minhsinh_booking_url', array(
        'default'   => '/booking/',
        'transport' => 'refresh',
    ));

    $wp_customize->add_control('minhsinh_booking_url_control', array(
        'label'    => __('URL Trang Đặt lịch (App/Django)', 'minhsinh-dental'),
        'section'  => 'minhsinh_system_section',
        'settings' => 'minhsinh_booking_url',
        'type'     => 'url',
    ));
}
add_action('customize_register', 'minhsinh_customize_register');


// =============================================================================
// 1. ĐIỀU HƯỚNG LIÊN KẾT TRANG ĐĂNG NHẬP & ADMIN BAR
// =============================================================================
function minhsinh_custom_login_links($html_link) {
    $admin_url = '/admin/';
    $web_url   = home_url('/');

    $output  = '<div class="minhsinh-login-nav" style="margin-top: 15px; display: flex; flex-direction: column; gap: 8px; text-align: center; font-size: 14px;">';
    $output .= '    <a href="' . esc_url($admin_url) . '" style="color: #2563eb; font-weight: 700; text-decoration: none; padding: 6px 12px; background: #eff6ff; border-radius: 6px; border: 1px solid #bfdbfe; display: block;">&larr; Về Trang Admin (Nha Khoa Minh Sinh)</a>';
    $output .= '    <a href="' . esc_url($web_url) . '" style="color: #059669; font-weight: 700; text-decoration: none; padding: 6px 12px; background: #ecfdf5; border-radius: 6px; border: 1px solid #a7f3d0; display: block;">Đi đến Web Nha Khoa Minh Sinh &rarr;</a>';
    $output .= '</div>';

    return $output;
}
add_filter('login_site_html_link', 'minhsinh_custom_login_links');

// Đổi URL và Tooltip khi bấm vào Logo trên trang đăng nhập WordPress
add_filter('login_headerurl', function() {
    return home_url('/');
});
add_filter('login_headertext', function() {
    return 'Nha Khoa Minh Sinh';
});

// Thêm nút chuyển nhanh trên Thanh công cụ Toolbar (Admin Bar) khi đăng nhập vào WordPress
function minhsinh_custom_admin_bar($wp_admin_bar) {
    $wp_admin_bar->add_node(array(
        'id'    => 'minhsinh_back_to_admin',
        'title' => '🏥 Về Trang Admin (Nha Khoa)',
        'href'  => '/admin/',
        'meta'  => array('target' => '_blank', 'title' => 'Chuyển về Trang Quản Trị Phòng Khám'),
    ));
    $wp_admin_bar->add_node(array(
        'id'    => 'minhsinh_go_to_web',
        'title' => '🌐 Đi đến Web',
        'href'  => home_url('/'),
        'meta'  => array('target' => '_blank', 'title' => 'Xem Trang Chủ Website Nha Khoa Minh Sinh'),
    ));
}
add_action('admin_bar_menu', 'minhsinh_custom_admin_bar', 100);


// =============================================================================
// 2. SINGLE SIGN-ON (SSO) TỰ ĐỘNG ĐĂNG NHẬP TỪ DJANGO ADMIN
// =============================================================================
define('MINHSINH_SSO_SECRET_KEY', 'minhsinh_dental_sso_secure_key_2026');

function minhsinh_handle_sso_login() {
    if (!isset($_GET['minhsinh_sso']) || empty($_GET['minhsinh_sso'])) {
        return;
    }

    $token = sanitize_text_field($_GET['minhsinh_sso']);
    $parts = explode('.', $token);
    if (count($parts) !== 2) {
        wp_die('Lỗi SSO: Định dạng token không hợp lệ.', 'Lỗi Xác Thực SSO', array('response' => 400));
    }

    list($b64_payload, $signature) = $parts;

    // 1. Xác thực chữ ký HMAC-SHA256
    $expected_sig = hash_hmac('sha256', $b64_payload, MINHSINH_SSO_SECRET_KEY);
    if (!hash_equals($expected_sig, $signature)) {
        wp_die('Lỗi SSO: Chữ ký xác thực không hợp lệ. Vui lòng thử lại từ trang Admin phòng khám.', 'Lỗi Xác Thực SSO', array('response' => 403));
    }

    // 2. Giải mã Payload JSON
    $padded_b64 = str_replace(array('-', '_'), array('+', '/'), $b64_payload);
    $json_payload = base64_decode($padded_b64);
    $data = json_decode($json_payload, true);

    if (!$data || !is_array($data)) {
        wp_die('Lỗi SSO: Dữ liệu payload không thể giải mã.', 'Lỗi Xác Thực SSO', array('response' => 400));
    }

    // 3. Kiểm tra thời hạn hiệu lực (60 giây)
    if (empty($data['exp']) || time() > $data['exp']) {
        wp_die('Lỗi SSO: Phiên xác thực đã hết hạn. Vui lòng bấm lại liên kết từ Django Admin.', 'Phiên Hết Hạn', array('response' => 403));
    }

    // 4. Phân quyền: Chỉ cho phép Administrator hoặc Editor/Author (Marketing)
    $allowed_roles = array('administrator', 'editor', 'author');
    $role = (!empty($data['r']) && in_array($data['r'], $allowed_roles, true)) ? $data['r'] : 'editor';

    $username = sanitize_user($data['u']);
    $email = sanitize_email(!empty($data['e']) ? $data['e'] : $username . '@minhsinh.vn');

    // 5. Tìm hoặc tạo User WordPress tương ứng
    $user = get_user_by('login', $username);
    if (!$user && !empty($email)) {
        $user = get_user_by('email', $email);
    }

    if (!$user) {
        // Tự động tạo user mới nếu chưa tồn tại
        $random_password = wp_generate_password(24, true, true);
        $user_id = wp_create_user($username, $random_password, $email);
        if (is_wp_error($user_id)) {
            wp_die('Lỗi tạo tài khoản SSO: ' . esc_html($user_id->get_error_message()), 'Lỗi SSO', array('response' => 500));
        }
        $user = get_user_by('id', $user_id);
    }

    // Đảm bảo cập nhật đúng role tương ứng với phân quyền
    if ($user && !in_array($role, (array) $user->roles, true)) {
        $user->set_role($role);
    }

    // 6. Đăng nhập và tạo Auth Cookie WordPress
    wp_clear_auth_cookie();
    wp_set_current_user($user->ID);
    wp_set_auth_cookie($user->ID, true);

    // 7. Chuyển hướng tới trang đích được yêu cầu (edit.php, post-new.php, upload.php,...)
    $target = !empty($data['t']) ? sanitize_text_field($data['t']) : 'edit.php';
    $redirect_url = admin_url($target);
    wp_safe_redirect($redirect_url);
    exit;
}
add_action('init', 'minhsinh_handle_sso_login', 1);


// =============================================================================
// 3. PHÂN QUYỀN CHẶT CHẼ: CHỈ ADMIN & MARKETING ĐƯỢC PHÉP TRUY CẬP WORDPRESS
// =============================================================================

// A. Chặn truy cập trực tiếp vào khu vực Quản trị (wp-admin) đối với các vai trò khác
function minhsinh_enforce_admin_access() {
    if (wp_doing_ajax()) {
        return;
    }

    if (is_admin()) {
        $user = wp_get_current_user();
        $allowed_roles = array('administrator', 'editor', 'author');
        $has_permission = array_intersect($allowed_roles, (array) $user->roles);

        if (!$has_permission) {
            wp_die(
                '<div style="font-family: system-ui, -apple-system, sans-serif; max-width: 500px; margin: 60px auto; padding: 30px; text-align: center; border-radius: 12px; background: #fff; box-shadow: 0 4px 20px rgba(0,0,0,0.1); border: 1px solid #fee2e2;">
                    <div style="font-size: 48px; margin-bottom: 12px;">🚫</div>
                    <h2 style="color: #991b1b; font-size: 20px; font-weight: 700; margin-bottom: 8px;">TRUY CẬP BỊ TỪ CHỐI</h2>
                    <p style="color: #4b5563; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                        Chỉ <strong>Quản trị viên (Admin)</strong> và <strong>Bộ phận Marketing</strong> mới có quyền truy cập hệ thống Bài viết & Blog Nha Khoa Minh Sinh.
                    </p>
                    <a href="/admin/" style="display: inline-block; padding: 8px 18px; background: #2563eb; color: #fff; text-decoration: none; border-radius: 6px; font-weight: 600; font-size: 13px;">&larr; Về Trang Quản Trị Phòng Khám</a>
                </div>',
                'Truy Cập Bị Từ Chối',
                array('response' => 403, 'back_link' => false)
            );
        }
    }
}
add_action('admin_init', 'minhsinh_enforce_admin_access');

// B. Chặn đăng nhập qua wp-login.php nếu tài khoản không thuộc Admin hoặc Marketing
function minhsinh_check_login_role($user, $username, $password) {
    if (is_wp_error($user) || empty($user)) {
        return $user;
    }

    $allowed_roles = array('administrator', 'editor', 'author');
    $user_roles = (array) $user->roles;
    $has_permission = array_intersect($allowed_roles, $user_roles);

    if (!$has_permission) {
        return new WP_Error(
            'role_not_allowed',
            '<strong>Từ chối truy cập:</strong> Tài khoản của bạn không thuộc bộ phận Quản trị (Admin) hoặc Marketing.'
        );
    }

    return $user;
}
add_filter('authenticate', 'minhsinh_check_login_role', 30, 3);


// =============================================================================
// 4. SCHEMA NHA KHOA CHUẨN GOOGLE (DENTIST / MEDICALBUSINESS JSON-LD)
// =============================================================================
function minhsinh_output_dental_schema() {
    $site_url = home_url('/');
    
    // Schema cơ sở phòng khám nha khoa chuẩn Google Search
    $schema = array(
        '@context'         => 'https://schema.org',
        '@type'            => 'Dentist',
        '@id'              => $site_url . '#dentist',
        'name'             => 'Nha Khoa Minh Sinh',
        'alternateName'    => 'Minh Sinh Dental Clinic Hanoi',
        'url'              => $site_url,
        'logo'             => $site_url . 'wp-content/themes/minhsinh-dental/screenshot.png',
        'image'            => $site_url . 'wp-content/themes/minhsinh-dental/screenshot.png',
        'description'      => 'Nha Khoa Minh Sinh - Hệ thống Nha khoa Y khoa Kỹ thuật cao tại Hà Nội. Chuyên sâu Cấy ghép Implant không đau, Niềng răng thẩm mỹ, Dán sứ Veneer và Bệnh án số 3D.',
        'medicalSpecialty' => 'Dentistry',
        'telephone'        => '+84-987-654-321',
        'priceRange'       => '$$',
        'currenciesAccepted' => 'VND',
        'paymentAccepted'  => 'Tiền mặt, Chuyển khoản ngân hàng, Thẻ tín dụng, Trả góp',
        'address'          => array(
            '@type'           => 'PostalAddress',
            'streetAddress'   => '46C Quán Sứ, Hàng Bông',
            'addressLocality' => 'Hoàn Kiếm',
            'addressRegion'   => 'Hà Nội',
            'postalCode'      => '100000',
            'addressCountry'  => 'VN',
        ),
        'geo'              => array(
            '@type'     => 'GeoCoordinates',
            'latitude'  => 21.028246,
            'longitude' => 105.846018,
        ),
        'hasMap'           => 'https://maps.google.com/?cid=5532454645229641304',
        'openingHoursSpecification' => array(
            array(
                '@type'     => 'OpeningHoursSpecification',
                'dayOfWeek' => array('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
                'opens'     => '08:00',
                'closes'    => '19:00',
            ),
        ),
    );

    // Nếu ở trang chi tiết bài viết, thêm Schema Article chuẩn y khoa
    if (is_single()) {
        global $post;
        $schema['@type'] = array('Dentist', 'MedicalWebPage');
        $schema['mainEntity'] = array(
            '@type'            => 'MedicalScholarlyArticle',
            'headline'         => get_the_title(),
            'datePublished'    => get_the_date('c'),
            'dateModified'     => get_the_modified_date('c'),
            'author'           => array(
                '@type' => 'Person',
                'name'  => get_the_author(),
            ),
            'publisher'        => array(
                '@type' => 'Organization',
                'name'  => 'Nha Khoa Minh Sinh',
                'url'   => $site_url,
            ),
            'description'      => wp_strip_all_tags(get_the_excerpt()),
            'medicalAudience'  => 'Patient',
        );
    }

    echo "\n<!-- MINH SINH DENTAL SCHEMA JSON-LD -->\n";
    echo '<script type="application/ld+json">' . json_encode($schema, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRETTY_PRINT) . "</script>\n";
}
add_action('wp_head', 'minhsinh_output_dental_schema', 5);
