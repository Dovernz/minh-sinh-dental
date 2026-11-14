-- 1. Nạp bài viết chuyên sâu từ database cũ
INSERT INTO wp_posts (
    post_author, post_date, post_date_gmt, post_content, post_title,
    post_excerpt, post_status, comment_status, ping_status, post_name,
    post_modified, post_modified_gmt, post_type, to_ping, pinged,
    post_content_filtered
) VALUES (
    1, NOW(), UTC_TIMESTAMP(), '<p style="text-align: center; line-height: 1.2;"><img src="https://res.cloudinary.com/ocsxoyvj/image/upload/v1788421739/cnragt1sjom32zrrtn3w.png" alt="Niềng răng sớm cho trẻ" width="337" height="450"></p>

<p style="line-height: 1.2;">Nhiều ba mẹ thường đợi đến khi con thay hết răng (khoảng 12-15 tuổi) mới bắt đầu nghĩ đến việc chỉnh nha. Tuy nhiên, dưới góc độ chuyên gia tại Minh Sinh Dental, việc "can thiệp sớm" từ giai đoạn 6-12 tuổi mới thực sự là món quà ý nghĩa nhất cho nụ cười tương lai của bé.</p>

<p style="line-height: 1.2;"><strong>Tại sao phải là "Niềng răng sớm"?</strong></p>

<p style="line-height: 1.2;">Thay vì đợi răng lệch lạc rồi mới sửa, niềng răng sớm (chỉnh nha tăng trưởng) giúp:</p>

<p style="line-height: 1.2;">- <strong>Điều hướng xương hàm:</strong> Khi xương của con còn đang phát triển, bác sĩ dễ dàng điều chỉnh vòm hàm, hạn chế tình trạng móm, hô hay lệch mặt mà không cần phẫu thuật sau này.</p>

<p style="line-height: 1.2;">- <strong>Tạo chỗ cho răng vĩnh viễn:</strong> Giúp các răng hằng thuận lợi mọc đúng vị trí, giảm thiểu tối đa việc phải nhổ răng khi chỉnh nha ở tuổi trưởng thành.</p>

<p style="line-height: 1.2;">- <strong>Loại bỏ thói quen xấu:</strong> Can thiệp kịp thời các tật đẩy lưỡi, mút tay – những "thủ phạm" thầm lặng làm biến dạng nụ cười của bé.</p>

<p style="line-height: 1.2;">Đây là nỗi lo lớn nhất của ba mẹ. Tại Minh Sinh Dental, chúng tôi áp dụng các loại khí cụ linh hoạt (như hàm Silicon hoặc khí cụ tháo lắp) cực kỳ nhẹ nhàng:</p>

<ul>
<li>Con vẫn ăn uống, vui chơi và phát biểu trên lớp tự tin.</li>
<li>Không cần nhổ răng, không gây áp lực mạnh lên xương hàm.</li>
<li>Thời gian đeo hàm linh hoạt, dễ dàng vệ sinh.</li>
</ul>

<p style="line-height: 1.2;"><strong>Lời khuyên từ Minh Sinh:</strong></p>

<p style="line-height: 1.2;">"Thời điểm vàng" để đưa bé đi tầm soát chỉnh nha là khi bé bắt đầu thay những chiếc răng cửa đầu tiên (khoảng 6-7 tuổi). Một cuộc thăm khám ngắn có thể giúp ba mẹ tiết kiệm được rất nhiều thời gian và chi phí cho con sau này.</p>

<p style="line-height: 1.2;">Hãy để con bước vào tuổi dậy thì với một diện mạo tự tin nhất!</p>

<p style="line-height: 1.2;"><strong>NHA KHOA MINH SINH | DI SẢN NỤ CƯỜI</strong></p>

<p style="line-height: 1.2;">📍 Cơ sở 1: 123 Phố Huế, Hai Bà Trưng, Hà Nội. Hotline: 0988 123 456</p>

<p style="line-height: 1.2;">📍 Cơ sở 2: 456 Nguyễn Trãi, Thanh Xuân, Hà Nội. Hotline: 0977 654 321</p>', 'CÓ NÊN NIỀNG RĂNG SỚM CHO CON?',
    'Chuyên gia Minh Sinh Dental chia sẻ về thời điểm vàng can thiệp chỉnh nha sớm cho trẻ từ 6-12 tuổi.', 'publish', 'open', 'open', 'co-nen-nieng-rang-som-cho-con',
    NOW(), UTC_TIMESTAMP(), 'post', '', '', ''
) ON DUPLICATE KEY UPDATE post_content = VALUES(post_content);

-- 2. Tự động khởi tạo trang /booking/ và gắn template page-booking.php
INSERT INTO wp_posts (
    ID, post_author, post_date, post_date_gmt, post_content, post_title,
    post_excerpt, post_status, comment_status, ping_status, post_name,
    post_modified, post_modified_gmt, post_type, to_ping, pinged,
    post_content_filtered
) VALUES (
    999, 1, NOW(), UTC_TIMESTAMP(), '', 'Đặt Lịch Hẹn',
    '', 'publish', 'closed', 'closed', 'booking',
    NOW(), UTC_TIMESTAMP(), 'page', '', '', ''
) ON DUPLICATE KEY UPDATE post_name = 'booking', post_status = 'publish';

INSERT INTO wp_postmeta (post_id, meta_key, meta_value) 
VALUES (999, '_wp_page_template', 'page-booking.php')
ON DUPLICATE KEY UPDATE meta_value = 'page-booking.php';
