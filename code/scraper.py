def run_scraper(search_id):
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
    cursor.execute('''
        SELECT url_link
        FROM results_table
        WHERE search_id = %s AND isSponsored = False
    ''', (search_id,))
    rows = cursor.fetchall()

    for row in rows:
        url = row['url_link']

        try:
            r = requests.get(url, allow_redirects=True, timeout=10)
            soup = BeautifulSoup(r.content, 'html.parser')
        except Exception as e:
            # print(f"Error scraping {url}: {e}")
            continue

        # Remove script/style tags
        for element in soup(['style', 'script']):
            element.extract()

        # Get visible text
        text = soup.get_text(separator=" ")
        text = re.sub(r"\s+", " ", text).strip()
        title_tag = soup.find('title')
        title = title_tag.get_text(strip=True) if title_tag else ''
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        cleaned_text = "\n".join(lines).lower()

        cursor.execute(''' 
            INSERT INTO content_info (
                search_id, url, info_type, content_details, title
            ) VALUES (%s, %s, 'text', %s,  %s)
        ''', (
            search_id,
            url,
            cleaned_text,
            title
        ))
        inserted_count += 1

    connection.commit()
    connection.close()
    #print(f"{inserted_count} pages saved to content_info table.")
