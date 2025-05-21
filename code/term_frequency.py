import mysql.connector
from mysql.connector import connect
import re
import string

def get_term_frequency(search_id):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="MY_CUSTOM_BOT",
        use_unicode=True,
        charset="utf8mb4"
    )

    cursor = connection.cursor(dictionary=True)

    # time to get search terms!
    cursor.execute("SELECT search_term FROM search_table WHERE search_id = %s", (search_id,))
    result = cursor.fetchone()

    insert_count = 0

    search_term = result['search_term'].lower()

    cursor.execute("""
        SELECT url, content_details
        FROM content_info
        WHERE search_id = %s AND (info_type = 'ocr_text' OR info_type = 'text')
    """, (search_id,))
    content_rows = cursor.fetchall()

    phrase_pattern = r'(?i)' + r'\s+'.join(map(re.escape, search_term.split()))

    for i, row in enumerate(content_rows):
        content = row['content_details'].lower()
        url = row['url']

        if url.startswith("screenshots/"):
            continue

        # Clean punctuation
        content = content.translate(str.maketrans('', '', string.punctuation))

        # --- PHRASE MATCH ---
        phrase_matches = len(re.findall(phrase_pattern, content))

        if phrase_matches > 0:
            cursor.execute('''
                INSERT INTO term_frequency (search_id, search_term, url, frequency)
                VALUES (%s, %s, %s, %s)
            ''', (search_id, search_term, url, phrase_matches))
            insert_count += 1

        # --- INDIVIDUAL WORD MATCHES ---
        for word in search_term.split():
            word_pattern = r'(?i)\b' + re.escape(word) + r'\b'
            word_matches = len(re.findall(word_pattern, content))

            if word_matches > 0:
                cursor.execute('''
                    INSERT INTO term_frequency (search_id, search_term, url, frequency)
                    VALUES (%s, %s, %s, %s)
                ''', (search_id, word, url, word_matches))
                insert_count += 1

        # Optional: log the first few rows for debug
        if i < 2:
            #print(f"[DEBUG] URL: {url}")
            #print(f"[DEBUG] Phrase matches: {phrase_matches}")
            #print(f"[DEBUG] Phrase pattern: {phrase_pattern}")
            for word in search_term.split():
                word_pattern = r'(?i)\b' + re.escape(word) + r'\b'
                count = len(re.findall(word_pattern, content))
                #print(f"[DEBUG] '{word}' -> {count}")

    connection.commit()
    cursor.close()
    connection.close()

    #print(f"Inserted keyword counts for {insert_count} results.")
