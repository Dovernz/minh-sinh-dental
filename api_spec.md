# API & System Design Specification

## 1. Database Schema Changes

### 1.1 Model `Employee` (app: `booking`)
Thêm trường **Loại hợp đồng** để phân loại bác sĩ tính hoa hồng.
- **Thêm field:**
  ```python
  CONTRACT_CHOICES = [
      ('Part-time', 'Part-time'),
      ('Full-time', 'Full-time'),
  ]
  contract_type = models.CharField(max_length=20, choices=CONTRACT_CHOICES, default='Full-time', verbose_name="Loại hợp đồng")
  ```

### 1.2 Model `BookingDetail` (app: `booking` - Kế hoạch Điều trị/Dịch vụ)
Thay thế trường `doctor` hiện tại bằng 2 trường: Bác sĩ tư vấn và Bác sĩ thực hiện.
Lưu trữ luôn mức hoa hồng tính được tại thời điểm tạo/cập nhật để bảo toàn dữ liệu lịch sử nếu đơn giá hoặc tỷ lệ hoa hồng thay đổi.
- **Xóa field:** `doctor`
- **Thêm fields:**
  ```python
  consulting_doctor = models.ForeignKey(
      "Employee", on_delete=models.SET_NULL, null=True, related_name="consulting_details",
      limit_choices_to={'role': 'Doctor'}, verbose_name="Bác sĩ tư vấn"
  )
  performing_doctor = models.ForeignKey(
      "Employee", on_delete=models.SET_NULL, null=True, related_name="performing_details",
      limit_choices_to={'role': 'Doctor'}, verbose_name="Bác sĩ thực hiện"
  )
  consulting_commission = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Hoa hồng BS tư vấn")
  performing_commission = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="Hoa hồng BS thực hiện")
  ```
- **Logic khi Save (Signal hoặc override `save()`):**
  - Nếu `consulting_doctor.contract_type == 'Part-time'`: `consulting_commission` = `actual_price * 0.05` (5%)
  - Nếu `performing_doctor.contract_type == 'Part-time'`: `performing_commission` = `actual_price * 0.10` (10%)
  - Trái lại (Full-time): Hoa hồng = 0.

---

## 2. API Endpoints

### 2.1 Quản lý Nhân viên (Thay thế Django Admin bằng Embed Modal)
Các API này sẽ được cung cấp cho Frontend (HTML/JS/Tailwind) để làm Modal quản lý nhân viên.
- `GET /api/employees/`: Lấy danh sách nhân viên. Có thể filter `?role=Doctor`.
- `GET /api/employees/{id}/`: Lấy thông tin chi tiết nhân viên.
- `POST /api/employees/`: Tạo mới nhân viên (yêu cầu điền họ tên, số ĐT, role, loại hợp đồng...).
- `PUT / PATCH /api/employees/{id}/`: Cập nhật nhân viên.
- `DELETE /api/employees/{id}/`: Xóa nhân viên (hoặc Deactivate).

### 2.2 Data cho Form Tạo Dịch vụ (Load data từ Backend)
Form tạo/sửa `BookingDetail` cần danh sách Bác sĩ và Dịch vụ.
- `GET /api/doctors/`:
  - **Mô tả:** Lấy danh sách Bác sĩ.
  - **Response:** Mảng các object `{"employee_id": 1, "full_name": "Nguyễn Văn A", "specialty": "Răng Hàm Mặt", "contract_type": "Part-time"}`.
- `GET /api/services-tree/`:
  - **Mô tả:** Lấy danh sách Dịch vụ (nhóm theo Danh mục) để render vào Dropdown/Cascader.
  - **Response:**
    ```json
    [
      {
        "category_id": 1,
        "name": "Nhổ răng",
        "services": [
          {"service_id": 10, "name": "Nhổ răng khôn", "price": 1000000},
          {"service_id": 11, "name": "Nhổ răng sữa", "price": 100000}
        ]
      }
    ]
    ```

### 2.3 Thống kê & Báo cáo
Menu mới: Thống kê dịch vụ đã tạo & Thống kê hoa hồng bác sĩ.

- **`GET /api/statistics/services/`** (Thống kê dịch vụ đã tạo)
  - **Query Params:** `?start_date=2026-09-01&end_date=2026-09-30`
  - **Response:** Danh sách các `BookingDetail` trong khoảng thời gian.
  - **Fields:** `detail_id`, `service_name`, `booking_id`, `actual_price`, `consulting_doctor_name`, `performing_doctor_name`, `created_on`.

- **`GET /api/statistics/commissions/`** (Thống kê hoa hồng bác sĩ)
  - **Query Params:** `?start_date=2026-09-01&end_date=2026-09-30`
  - **Logic:** Nhóm các `BookingDetail` theo Bác sĩ (chỉ áp dụng cho Part-time có phát sinh hoa hồng).
  - **Response:**
    ```json
    [
      {
        "doctor_id": 2,
        "doctor_name": "Trần Thị B",
        "total_consulting_commission": 500000,
        "total_performing_commission": 2000000,
        "total_commission": 2500000
      }
    ]
    ```

---

## 3. Security Rules & Permissions
- Các endpoint `/api/employees/` yêu cầu quyền `Admin`.
- Các endpoint `/api/doctors/` và `/api/services-tree/` yêu cầu xác thực (`IsAuthenticated`), có thể là Admin hoặc Lễ tân/Bác sĩ.
- Các endpoint `/api/statistics/` yêu cầu quyền `Admin` hoặc Role tương đương có quyền xem báo cáo tài chính/hoa hồng.
- Bác sĩ (Part-time/Full-time) nếu đăng nhập chỉ được xem thống kê hoa hồng của chính mình, không được xem của người khác (áp dụng Filter theo `request.user.employee_profile`).
