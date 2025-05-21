# The purpose of this .py file is to find and label media content that isn't sponsored.

def media_detection():
    import os
    import re
    import requests
    from bs4 import BeautifulSoup
    import mysql.connector
    from mysql.connector import connect, Error
    from mysql.connector.cursor import MySQLCursorDict
    import urllib.parse

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="MY_CUSTOM_BOT",
        use_unicode=True,
        charset="utf8mb4"
    )
    cursor = connection.cursor(dictionary=True)

    media_extensions = {
        "pdf": "PDF", "doc": "Word Document", "docx": "Word Document",
        "xls": "Excel Spreadsheet", "xlsx": "Excel Spreadsheet",
        "ppt": "PowerPoint", "pptx": "PowerPoint", "txt": "Text File",
        "csv": "CSV File", "rtf": "Rich Text Format", "odt": "OpenDocument Text",
        "jpg": "Image", "jpeg": "Image", "png": "Image", "gif": "Image",
        "webp": "Image", "bmp": "Image", "tiff": "Image", "svg": "Vector Image",
        "mp3": "Audio", "wav": "Audio", "m4a": "Audio", "flac": "Audio", "aac": "Audio",
        "mp4": "Video", "mov": "Video", "avi": "Video", "mkv": "Video",
        "webm": "Video", "wmv": "Video", "zip": "Archive", "rar": "Archive",
        "7z": "Archive", "tar": "Archive", "gz": "Archive", "tar.gz": "Archive",
        "html": "HTML Document", "css": "Stylesheet", "js": "JavaScript File",
        "json": "JSON Data", "xml": "XML Data", "py": "Python Script", "ipynb": "Jupyter Notebook"
    }

    inserted_count = 0
    cursor.execute('SELECT * FROM results_table WHERE isSponsored = False')
    rows = cursor.fetchall()

    MAX_MEDIA_ROWS = 20

    for i, row in enumerate(rows):
        if i >= MAX_MEDIA_ROWS:
            break

        search_id = row['search_id']
        url = row['url_link']

    # for row in rows:
    #     search_id = row['search_id']
    #     url = row['url_link']

        try:
            r = requests.get(url, allow_redirects=True, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

        a_tag = soup.find_all('a', href=re.compile(r'\.[a-zA-Z0-9]{2,5}$'))
        img_tag = soup.find_all('img', src=re.compile(r'\.[a-zA-Z0-9]{2,5}$'))

        for a in a_tag:
            href = a.get('href')
            if not href:
                continue
            media_url = urllib.parse.urljoin(url, href)
            _, ext = os.path.splitext(media_url)
            ext = ext.strip(".").lower()
            media_type = media_extensions.get(ext, "Other File")

            cursor.execute(''' 
                INSERT INTO media_output (search_id, url, media_url, media_type)
                VALUES (%s, %s, %s, %s)
            ''', (search_id, url, media_url, media_type))
            inserted_count += 1

        for img in img_tag:
            src = img.get('src')
            if not src:
                continue
            media_url = urllib.parse.urljoin(url, src)
            _, ext = os.path.splitext(media_url)
            ext = ext.strip(".").lower()
            media_type = media_extensions.get(ext, "Other File")
            cursor.execute(''' 
                INSERT INTO media_output (search_id, url, media_url, media_type)
                VALUES (%s, %s, %s, %s)
            ''', (search_id, url, media_url, media_type))
            inserted_count += 1

    connection.commit()
    connection.close()
    #print(f"{inserted_count} media files saved to media_output table.")
