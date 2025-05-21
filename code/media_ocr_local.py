import os
import requests
import tempfile
from bs4 import BeautifulSoup
from pdf2image import convert_from_path
from PIL import Image
import pytesseract
import mysql.connector


from config import tesseract_path

pytesseract.pytesseract.tesseract_cmd = tesseract_path

def extract_text_from_pdf_url(url):
    try:
        response = requests.get(url, stream=True, timeout=10)
        response.raise_for_status()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_pdf:
            temp_pdf.write(response.content)
            temp_pdf_path = temp_pdf.name

        images = convert_from_path(temp_pdf_path)
        full_text = "\n".join(pytesseract.image_to_string(img) for img in images)

        os.remove(temp_pdf_path)
        return full_text

    except Exception as e:
        return f"PDF OCR failed: {e}"

def extract_text_from_image_url(url):
    try:
        response = requests.get(url, stream=True, timeout=10)
        img = Image.open(response.raw)
        return pytesseract.image_to_string(img)
    except Exception as e:
        return f"Image OCR failed: {e}"

def ocr_processing(search_id):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="MY_CUSTOM_BOT",
        use_unicode=True,
        charset="utf8mb4"
    )
    cursor = connection.cursor(dictionary=True)

    cursor.execute('''
        SELECT search_id, url, media_id, media_type
        FROM media_output
        WHERE media_type IN ("PDF", "Image")
    ''')
    rows = cursor.fetchall()
    inserted = 0

    for i, row in enumerate(rows):
        if i >= 5:
            break  # limting ocr here to bring run time down from 40+ minutes

        search_id = row["search_id"]
        url = row["url"]
        media_type = row["media_type"]

        # debugging 
        #print(f"OCR processing [{i+1}/{len(rows)}]: {url}")
        
        if media_type == "PDF":
            ocr_text = extract_text_from_pdf_url(url)
        else:
            ocr_text = extract_text_from_image_url(url)

        if ocr_text.strip():
            cursor.execute('''
                INSERT INTO content_info (search_id, url, info_type, content_details)
                VALUES (%s, %s, %s, %s)
            ''', (search_id, url, "ocr_text", ocr_text))
            inserted += 1

    connection.commit()
    connection.close()
    #print(f"OCR complete. Inserted {inserted} entries into content_info.")
