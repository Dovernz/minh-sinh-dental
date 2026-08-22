# Hoàn thành Nâng cấp Thanh toán & Phân quyền Admin

Hệ thống đã được thiết lập thành công theo đúng 2 yêu cầu mở rộng của bạn. Dưới đây là các chi tiết kỹ thuật đã được thay đổi.

## 1. Hệ thống cấu hình Thanh toán (VietQR)
- Đã tạo bảng vật lý `PaymentConfig` (`db_table_payment_config`) để lưu thông tin ngân hàng.
- **Tính năng độc quyền**: Model này đã được ghi đè phương thức `save()`. Bất cứ khi nào bạn lưu một tài khoản với `is_default=True`, các tài khoản khác tự động bị chuyển về `False`.
- **API tạo VietQR**: Đã mở một endpoint mới tại `GET /api/payment-info/?amount=<tien>&note=<ghi_chu>`. API này sẽ trả về cục JSON chứa toàn bộ thông tin ngân hàng mặc định cùng với URL mã QR trực tiếp từ VietQR (`https://img.vietqr.io/image/...`). 

## 2. Bác sĩ & SQL View mới
- Bảng `Booking` gốc đã có thêm trường `doctor` (kiểu Dropdown, cho phép trống).
- Đã xóa View ảo SQL cũ và nạp lại bằng một View mới hoàn thiện hơn, JOIN thành công bảng Nhân viên để kéo ra trường `doctor_name`.
- Trong giao diện admin, `BookingDetailsView` giờ đây đã có thêm cột **Bác sĩ khám** trên danh sách, và có thể Filter trực tiếp theo tên Bác sĩ.

## 3. Phân quyền Admin (RBAC) chặt chẽ
Đã cấu hình các lớp phân quyền cứng trong `admin.py`:
- **Admin / Superuser**: Nhìn thấy toàn bộ tính năng CRUD cho mọi bảng vật lý.
- **Nhóm "Staff" (Lễ tân)**: Bị cắt đứt quyền sửa (`change`) và xóa (`delete`) đối với `Booking`, `Clinic`, `Service`, và `PaymentConfig`.
- Tại trang chi tiết Booking, lễ tân **vẫn có thể Thêm mới (Add)** trạng thái vào `BookingStatus` và nạp hóa đơn vào `Payment` thông qua các TabularInline. Tuy nhiên, tính năng an toàn sẽ khóa hoàn toàn không cho sửa/xóa các trạng thái/hóa đơn cũ đã được lưu, bảo toàn tính lịch sử tuyệt đối.
