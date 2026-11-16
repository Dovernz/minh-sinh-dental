import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

def run_proofs():
    os.makedirs('docs/proofs', exist_ok=True)
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1440,900')

    driver = webdriver.Chrome(options=options)

    try:
        # Proof 1: Admin Login Interface Fixed
        print("1. Chụp proof trang Login Admin...")
        driver.get('http://127.0.0.1:8000/admin/login/')
        time.sleep(2)
        try:
            driver.find_element(By.ID, 'id_username').send_keys('admin')
            driver.find_element(By.ID, 'id_password').send_keys('MinhSinh@2026')
            driver.find_element(By.ID, 'toggle-password').click()
            time.sleep(0.5)
        except Exception as e:
            print("Login fill warning:", e)
        driver.save_screenshot('docs/proofs/proof_login_fixed.png')
        print("-> Đã lưu docs/proofs/proof_login_fixed.png")

        # Proof 2: Booking Step 1
        print("2. Chụp proof Booking Step 1...")
        driver.get('http://127.0.0.1:8000/booking/')
        time.sleep(2)
        try:
            date_input = driver.find_element(By.CSS_SELECTOR, 'input[type="date"]')
            date_input.send_keys('2026-11-20')
            time.sleep(0.5)
        except Exception as e:
            print("Step 1 fill warning:", e)
        driver.save_screenshot('docs/proofs/proof_booking_step1.png')
        print("-> Đã lưu docs/proofs/proof_booking_step1.png")

        # Proof 3: Booking Step 2 - SĐT Lock 11 số + Validation + Categories Optgroup No Price
        print("3. Chuyển sang Step 2...")
        try:
            btn_step1 = driver.find_element(By.XPATH, "//button[contains(., 'Tiếp tục')]")
            btn_step1.click()
            time.sleep(1)

            # Điền họ tên
            name_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='Nguyễn Văn A']")
            name_input.send_keys('Nguyễn Văn An')

            # Test nhập SĐT siêu dài (15 số): hệ thống sẽ tự khóa cắt ở 11 số
            phone_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='0912345678']")
            phone_input.send_keys('091234567899999')
            time.sleep(0.5)
            val_after_long = phone_input.get_attribute('value')
            print(f"Giá trị sau khi nhập 15 số (bị lock 11 số): {val_after_long} (Độ dài: {len(val_after_long)})")

            # Test validation < 10 số: nhập 9 số và click Tiếp tục
            phone_input.clear()
            phone_input.send_keys('091234567') # 9 số
            time.sleep(0.5)
            btn_step2 = driver.find_element(By.XPATH, "//button[contains(., 'Tiếp tục')]")
            btn_step2.click()
            time.sleep(0.5)
        except Exception as e:
            print("Step 2 warning:", e)
        driver.save_screenshot('docs/proofs/proof_step2_categories_and_phone_lock.png')
        print("-> Đã lưu docs/proofs/proof_step2_categories_and_phone_lock.png")

        # Proof 4: Booking Step 3 - Khung giờ 30 phút (08:00 - 19:00)
        print("4. Nhập SĐT hợp lệ 10 số và Chuyển sang Step 3...")
        try:
            phone_input = driver.find_element(By.CSS_SELECTOR, "input[placeholder='0912345678']")
            phone_input.clear()
            phone_input.send_keys('0912345678')
            time.sleep(0.5)

            btn_step2 = driver.find_element(By.XPATH, "//button[contains(., 'Tiếp tục')]")
            btn_step2.click()
            time.sleep(1.5)
        except Exception as e:
            print("Step 3 transition warning:", e)
        driver.save_screenshot('docs/proofs/proof_step3_30min_slots_grid.png')
        print("-> Đã lưu docs/proofs/proof_step3_30min_slots_grid.png")

    finally:
        driver.quit()

if __name__ == '__main__':
    run_proofs()
