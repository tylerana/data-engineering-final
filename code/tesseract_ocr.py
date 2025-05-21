# This .py file does local OCR using Tesseract and handles screenshots

import pytesseract
from PIL import Image
from config import tesseract_path

def extract_text(image_path):
    try:
        return pytesseract.image_to_string(Image.open(image_path), lang='eng')
    except Exception as e:
        return f"Error extracting text: {e}"

def run_tesseract_ocr(search_id):
    import requests
    from bs4 import BeautifulSoup
    import mysql.connector
    from mysql.connector import connect, Error
    from mysql.connector.cursor import MySQLCursorDict
    import re

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="MY_CUSTOM_BOT",
        use_unicode=True,
        charset="utf8mb4"
    )
    cursor = connection.cursor(dictionary=True)

    inserted_count = 0

    cursor.execute('SELECT * FROM ocr_screenshots WHERE search_id = %s', (search_id,))
    rows = cursor.fetchall()

    for row in rows:
        url = row['screenshot_path']
        ocr_text = row['ocr_data']

        if not ocr_text or not ocr_text.strip():
            continue

        cursor.execute('''
            INSERT INTO content_info (
                search_id, url, info_type, content_details 
            ) VALUES (%s, %s, %s, %s) 
        ''', (
            search_id, 
            url, 
            "ocr_text",
            ocr_text.strip().lower()
        ))
        inserted_count += 1

    connection.commit()
    connection.close()
    #print(f"{inserted_count} entries added to content_info table from local OCR (tesseract).") 