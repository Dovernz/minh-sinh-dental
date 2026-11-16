import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_DIR = r"D:\Thành\WEB\Code\dental_project"
PROOFS_DIR = os.path.join(BASE_DIR, "docs", "proofs")
os.makedirs(PROOFS_DIR, exist_ok=True)

proof1_path = os.path.join(PROOFS_DIR, "pnr_admin_sidebar_search.png")
proof2_path = os.path.join(PROOFS_DIR, "pnr_admin_result_board.png")
proof3_path = os.path.join(PROOFS_DIR, "pnr_admin_interactive_action.png")

options = Options()
options.add_argument('--headless=new')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1600,1100')

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

try:
    print("[1] Logging into Django Admin...")
    driver.get("http://127.0.0.1:8000/admin/login/")
    time.sleep(1)

    username_input = wait.until(EC.presence_of_element_located((By.NAME, "username")))
    password_input = driver.find_element(By.NAME, "password")
    username_input.clear()
    username_input.send_keys("admin")
    password_input.clear()
    password_input.send_keys("admin123")

    submit_btn = driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
    submit_btn.click()
    time.sleep(2)
    print(f"Logged in, current URL: {driver.current_url}")

    print("[2] Navigating to PNR Lookup page (Sidebar + Search UI)...")
    driver.get("http://127.0.0.1:8000/admin/pnr-lookup/")
    time.sleep(2)

    # Proof 1: Menu sidebar + Màn hình tra cứu PNR ban đầu
    driver.save_screenshot(proof1_path)
    print(f"-> Proof 1 saved: {proof1_path} ({os.path.getsize(proof1_path):,} bytes)")

    print("[3] Searching PNR code MSLIVE1 via direct query navigation...")
    driver.get("http://127.0.0.1:8000/admin/pnr-lookup/?pnr=MSLIVE1")
    time.sleep(2)

    # Proof 2: Kết quả tra cứu PNR thẻ Boarding Pass + Thống kê VNĐ + Bảng khách hàng có nút thao tác
    driver.save_screenshot(proof2_path)
    print(f"-> Proof 2 saved: {proof2_path} ({os.path.getsize(proof2_path):,} bytes)")

    print("[4] Triggering interactive action: Open payment modal for individual customer...")
    driver.execute_script("""
        if (typeof openPayItemModal === 'function') {
            openPayItemModal('213', 'Nguyen Thi Lan', '300000');
        } else {
            console.error('openPayItemModal function not found');
        }
    """)
    time.sleep(1)

    # Proof 3: Thao tác thanh toán riêng lẻ / đổi trạng thái (Modal thu tiền hiển thị trực quan)
    driver.save_screenshot(proof3_path)
    print(f"-> Proof 3 saved: {proof3_path} ({os.path.getsize(proof3_path):,} bytes)")

    print("ALL PROOFS CAPTURED SUCCESSFULLY!")

finally:
    driver.quit()
