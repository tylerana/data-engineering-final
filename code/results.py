# The purpose of this function is to insert cleaned text to the content_info table

def run_results():
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
    
    # fetch all records from scraped_info
    inserted_count = 0

    cursor.execute('SELECT * FROM scrape_info')
    rows = cursor.fetchall()

    for row in rows:
        search_id = row['search_id']
        url = row['url']
        cleaned_text = row['cleaned_text']
        
        info_type = "cleaned_text"
        content_details = cleaned_text

        cursor.execute('''
            INSERT INTO content_info (
                search_id, url, info_type, content_details
            ) VALUES (%s, %s, %s, %s) 
        ''', (
            search_id, 
            url,
            info_type,
            content_details
        ))
        inserted_count+=1

    connection.commit()
    connection.close()

    #print(f"{inserted_count} entries added to content_info table.")

