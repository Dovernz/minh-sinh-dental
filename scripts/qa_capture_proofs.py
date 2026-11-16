import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def capture_proofs():
    # Tạo thư mục lưu ảnh nếu chưa tồn tại
    os.makedirs('docs/proofs', exist_ok=True)

    # Cấu hình Chrome Headless
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1440,900')

    driver = webdriver.Chrome(options=options)

    try:
        # Bước 1: Login & Toggle Password
        try:
            print("Đang thực hiện Bước 1: Login & Toggle Password...")
            driver.get('http://127.0.0.1:8000/admin/login/')
            
            driver.find_element(By.ID, 'id_username').send_keys('admin')
            driver.find_element(By.ID, 'id_password').send_keys('MinhSinh@2025')
            
            # Click nút hiện password
            driver.find_element(By.CSS_SELECTOR, '#toggle-password').click()
            time.sleep(1)
            
            driver.save_screenshot('docs/proofs/proof_7a_login_eye_toggle.png')
            print("-> Đã lưu proof_7a_login_eye_toggle.png")
        except Exception as e:
            print(f"Lỗi ở Bước 1: {e}")

        # Bước 2: Submit login & vào Dashboard
        try:
            print("Đang thực hiện Bước 2: Submit login...")
            # Tìm nút submit của form hoặc click trực tiếp button submit
            submit_btn = driver.find_element(By.CSS_SELECTOR, 'form input[type="submit"], form button[type="submit"], .submit-row input')
            submit_btn.click()
            time.sleep(2)
            
            driver.save_screenshot('docs/proofs/proof_7b_login_success_dashboard.png')
            print("-> Đã lưu proof_7b_login_success_dashboard.png")
        except Exception as e:
            print(f"Lỗi ở Bước 2: {e}")

        # Bước 3: Booking form
        try:
            print("Đang thực hiện Bước 3: Mở trang Booking...")
            driver.get('http://127.0.0.1:8000/booking/')
            time.sleep(2)
            
            driver.save_screenshot('docs/proofs/proof_1_booking_form_pnr_multi_customers.png')
            print("-> Đã lưu proof_1_booking_form_pnr_multi_customers.png")
        except Exception as e:
            print(f"Lỗi ở Bước 3: {e}")

        # Bước 4: Admin booking embed (Timeline grid matrix)
        try:
            print("Đang thực hiện Bước 4: Mở Timeline Grid Matrix...")
            driver.get('http://127.0.0.1:8000/admin/booking-embed/')
            time.sleep(2)
            
            driver.save_screenshot('docs/proofs/proof_2_timeline_grid_matrix.png')
            print("-> Đã lưu proof_2_timeline_grid_matrix.png")
        except Exception as e:
            print(f"Lỗi ở Bước 4: {e}")

        # Bước 5: API capacity check
        try:
            print("Đang thực hiện Bước 5: Kiểm tra Capacity Warning API...")
            driver.get('http://127.0.0.1:8000/api/capacity-check/?clinic_id=1&date=2026-11-20&start_time=09:00&passenger_count=15')
            time.sleep(1)
            
            driver.save_screenshot('docs/proofs/proof_3_capacity_warning.png')
            print("-> Đã lưu proof_3_capacity_warning.png")
        except Exception as e:
            print(f"Lỗi ở Bước 5: {e}")

        # Bước 6: E-ticket boarding pass
        try:
            print("Đang thực hiện Bước 6: Mở E-ticket...")
            driver.get('http://127.0.0.1:8000/booking/success/1/')
            time.sleep(2)
            
            driver.save_screenshot('docs/proofs/proof_4_eticket_boarding_pass.png')
            print("-> Đã lưu proof_4_eticket_boarding_pass.png")
        except Exception as e:
            print(f"Lỗi ở Bước 6: {e}")

        # Bước 7: Admin PNR quick lookup
        try:
            print("Đang thực hiện Bước 7: Mở PNR Quick Lookup...")
            driver.get('http://127.0.0.1:8000/admin/pnr-lookup/')
            time.sleep(2)
            
            driver.save_screenshot('docs/proofs/proof_5_admin_pnr_quick_lookup.png')
            print("-> Đã lưu proof_5_admin_pnr_quick_lookup.png")
        except Exception as e:
            print(f"Lỗi ở Bước 7: {e}")

        # Bước 8: Admin POS cashier payment
        try:
            print("Đang thực hiện Bước 8: Mở POS System...")
            driver.get('http://127.0.0.1:8000/admin/pos-system/')
            time.sleep(2)
            
            driver.save_screenshot('docs/proofs/proof_6_admin_pos_cashier_payment.png')
            print("-> Đã lưu proof_6_admin_pos_cashier_payment.png")
        except Exception as e:
            print(f"Lỗi ở Bước 8: {e}")

    finally:
        print("Đang đóng trình duyệt...")
        driver.quit()

if __name__ == '__main__':
    capture_proofs()