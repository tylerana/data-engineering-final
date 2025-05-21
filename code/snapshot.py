# This .py file takes screenshots
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from config import screenshot_folder
from tesseract_ocr import extract_text
import mysql.connector

def take_screenshot(url, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--start-maximized")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.set_page_load_timeout(30) 

    url = url.strip()

    try:
        if url.startswith("http://") or url.startswith("https://"):
            try:
                driver.get(url)
                driver.save_screenshot(output_path)
            except Exception as e:
                print(f"[WARNING] Failed to load {url}: {e}")
                return
        else:
            print(f"[WARNING] Skipping invalid URL: {url}")
            return
    finally:
        driver.quit()



def capture_and_ocr_screenshots(search_id, urls, max_screenshots=4):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="MY_CUSTOM_BOT",
        use_unicode=True, 
        charset="utf8mb4"
    )
    cursor = connection.cursor(dictionary=True)

    for i, url in enumerate(urls[:max_screenshots]):
        screenshot_path = f"{screenshot_folder}/screenshot_{search_id}_{i}.png"
        take_screenshot(url, screenshot_path)
        ocr_text = extract_text(screenshot_path)

        cursor.execute('''
            INSERT INTO ocr_screenshots (search_id, screenshot_path, ocr_data)
            VALUES (%s, %s, %s)
        ''', (search_id, screenshot_path, ocr_text))

    connection.commit()
    connection.close()
    #print(f"Screenshots and OCR complete for search_id={search_id}")

        