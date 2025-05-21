import sys
from datetime import datetime
import mysql.connector
import time
import pickle
import os

from config import screenshot_folder
from crawler import get_urls, urls_to_results_table, run_search
from snapshot import capture_and_ocr_screenshots
from scraper import run_scraper
from results import run_results
from media_scraper import media_detection
from media_ocr_local import ocr_processing
from tesseract_ocr import run_tesseract_ocr
from term_frequency import get_term_frequency
import functools

pipeline_start = time.time()

print = functools.partial(print, flush=True)
# === Read CLI args ===
now = datetime.now()

if len(sys.argv) < 3:
    print("Usage: python main.py <search_term> <engine>")
    sys.exit(1)

search_term = sys.argv[1]
engine = sys.argv[2]

# Automatically set num_results
if engine == "google":
    num_results = 100
else:
    num_results = None 

max_screenshots = 4

# === Search: get URLs from engine ===
urls = get_urls(search_term, engine, num_results)

if not urls:
    print("[INFO] No URLs found.")
    exit()

# === DB Connection ===
#print("Connecting to MySQL...")
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="MY_CUSTOM_BOT",
    use_unicode=True,
    charset="utf8mb4"
)
cursor = connection.cursor(dictionary=True)
# === Log search ===
cursor.execute('''
    INSERT INTO search_table (search_term, search_engine, num_results, search_date, search_time)
    VALUES (%s, %s, %s, %s, %s)
''', (search_term.strip().lower(), engine, num_results, now.strftime('%Y-%m-%d %H:%M:%S'), now.time().strftime('%H.%M')))
connection.commit()
search_id = cursor.lastrowid
connection.close()
#print(f"search={search_id} created in search_table.")


#print("Starting run_search()...")
run_search(search_term, engine, num_results, search_id)
#print("run_search() complete.")


#print("Starting run_scraper()...")
run_scraper(search_id)
#print("run_scraper() complete.")

# === Screenshots + Tesseract OCR ===
#print("Capturing screenshots and running limited OCR...")
capture_and_ocr_screenshots(search_id, urls)
#print("Screenshots captured and OCR (Tesseract) applied.")


# media detection
#print("Running media detection...")
media_detection()
#print("media_detection() complete.")

# inserting tesseract ocr into content_info
#print("Running final tesseract OCR insert into content_info...")
run_tesseract_ocr(search_id)
#print("run_tesseract_ocr() complete.")

# pdf2img for media_output
#print("Running ocr_processing...")
ocr_processing(search_id)
#print("ocr_processing() complete.")

# compute term frequency
#print("Computing term frequency...")
get_term_frequency(search_id)
#print("Term frequency complete")

# checking on rows inserted
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="MY_CUSTOM_BOT",
    use_unicode=True,
    charset="utf8mb4"
)

cursor = connection.cursor(dictionary=True)
cursor.execute("SELECT COUNT(*) AS count FROM term_frequency WHERE search_id = %s", (search_id,))
count = cursor.fetchone()['count']
cursor.close()
connection.close()

duration = time.time() - pipeline_start
mins = int(duration // 60)
secs = int(duration % 60)
print(f"\n Pipeline completed in {mins}m {secs}s")
