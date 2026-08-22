# Kế hoạch Nâng cấp Admin & Thanh toán

Dựa trên yêu cầu của bạn, tôi sẽ thực hiện 2 tính năng lớn: Cấu hình tài khoản ngân hàng động và Phân quyền Django Admin.

## 1. Hệ thống Cấu hình Thanh toán (PaymentConfig)
*   **Tạo Model `PaymentConfig`**: Bảng này sẽ lưu trữ `bank_name` (Mã ngân hàng, VD: VCB, MB), `account_number`, `account_name` và `is_default` (Boolean).
*   **Logic Độc quyền (Signal / Save override)**: Tôi sẽ ghi đè phương thức `save()` của model này. Nếu một bản ghi được lưu với `is_default=True`, hệ thống sẽ tự động cập nhật tất cả các bản ghi khác thành `is_default=False`. Điều này đảm bảo chỉ có duy nhất 1 tài khoản mặc định.
*   **Logic tạo QR Code VietQR**: Sẽ có một hàm tĩnh (hoặc property) dùng để sinh ra URL mã QR. Dựa vào API của VietQR, đường dẫn thường có dạng:
    `https://img.vietqr.io/image/<bank_name>-<account_number>-compact2.png?amount=<amount>&addInfo=<note>&accountName=<account_name>`
    Tôi sẽ tạo một API hoặc hàm để tự động thay các biến này dựa trên bản ghi `PaymentConfig` mặc định.

## 2. Phân quyền Admin (Role-Based Access Control)
Tôi sẽ cấu hình lại `admin.py` dựa trên các quyền (Permissions) mặc định của Django:

*   **Superuser / Admin Group**: Mặc định Superuser có toàn quyền. Đối với Group "Admin", bạn chỉ cần check vào ô cấp quyền hoặc tôi có thể code cứng logic (chỉ Superuser hoặc ai thuộc nhóm Admin mới thấy nút Add/Change/Delete ở các bảng gốc).
*   **Nhóm Lễ tân (Staff)**: 
    *   Sử dụng hàm `has_add_permission`, `has_change_permission`, `has_delete_permission` trong các file cấu hình `ModelAdmin`.
    *   Nếu người dùng thuộc nhóm "Staff" (Lễ tân) mà không phải Superuser/Admin, họ sẽ **bị False (chặn)** quyền Change/Delete ở các bảng vật lý gốc (`Booking`, `Clinic`, `Service`, `PaymentConfig`).
    *   Họ được phép **View** bảng `BookingDetails` (View ảo SQL).
    *   Họ được phép **Add/Change** trong các Inline của `BookingStatus` và `Payment` để cập nhật trạng thái hoặc thu tiền khách.

---
> [!IMPORTANT]
> **Câu hỏi để chốt phương án:**
> 1. Hiện tại backend chưa có endpoint API nào trả về thông tin VietQR này cho Frontend (React). Bạn muốn tôi làm 1 API riêng `/api/payment-qr/` để Frontend gọi và lấy Link ảnh QR, hay bạn muốn tôi viết một property sinh URL trực tiếp trong Model `Payment`?
> 2. URL tạo QR của VietQR chuẩn thường dùng host `img.vietqr.io`. Bạn ghi `https://vietqr.app/img?`, đây là bạn viết tắt hay là một dịch vụ cụ thể mà bạn đang dùng? Tôi sẽ dùng chuẩn của `vietqr.io` nhé?

Hãy nhấn **Proceed** hoặc phản hồi nếu bạn đồng ý với kế hoạch trên!
