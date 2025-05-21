# The purpose of this .py file is to search and insert URLs.

import requests
from bs4 import BeautifulSoup
from googlesearch import search as google_search
from duckduckgo_search import DDGS
import time
    
def get_links(url):
    """
    Extract all <a href> tags from the given URL.
    Returns a list of <a> tag elements.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.find_all('a', href=True)
    except Exception as e:
        print(f"Error fetching or parsing {url}: {e}")
        return []


def search_google(query, num_results=10):
    try:
        if num_results is None or num_results > 100:
            num_results = 100
        return list(google_search(query, num_results=num_results))
    except Exception as e:
        print(f"Google search failed: {e}")
        return []


def search_bing(query, num_results=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    page = 0
    while True:
        start = page * 10 + 1  # Bing shows 10 per page
        url = f"https://www.bing.com/search?q={query.replace(' ', '+')}&first={start}"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a['href'] for a in soup.select("li.b_algo h2 a") if a['href'].startswith("http")]
        if not links:
            break
        results.extend(links)
        page += 1
        if num_results and len(results) >= num_results:
            break
    return list(dict.fromkeys(results))


def search_yahoo(query, num_results=None):
    headers = {"User-Agent": "Mozilla/5.0"}
    results = []
    page = 0
    while True:
        start = page * 10 + 1
        url = f"https://search.yahoo.com/search?p={query.replace(' ', '+')}&b={start}"
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = [a['href'] for a in soup.select("h3.title a") if a['href'].startswith("http")]
        if not links:
            break
        results.extend(links)
        page += 1
        if num_results and len(results) >= num_results:
            break
    return list(dict.fromkeys(results))

def search_duckduckgo(query, num_results):
    with DDGS() as ddgs:
        for attempt in range(3):
            try:
                results = ddgs.text(query, max_results=num_results)
                return [r["href"] for r in results if "href" in r]
            except Exception as e:
                print(f"DuckDuckGo search failed (attempt {attempt+1}): {e}")
                time.sleep(2 * (attempt + 1))
        return []
    
def get_urls(search_term, engine, num_results):
    if engine == "Google":
        return search_google(search_term, num_results=num_results)
    elif engine == "Bing":
        return search_bing(search_term, num_results=num_results)
    elif engine == "Yahoo":
        return search_yahoo(search_term, num_results=num_results)
    elif engine == "DuckDuckGo":
        return search_duckduckgo(search_term, num_results=num_results)
    else:
        raise ValueError(f"Unsupported search engine: {engine}")
    

def urls_to_results_table(search_id, urls, cursor):
    inserted_count = 0
    for url in set(urls):
        cursor.execute('''
            SELECT COUNT(*) as count FROM results_table
            WHERE search_id = %s AND url_link = %s
        ''', (search_id, url))
        if cursor.fetchone()['count'] > 0:
            continue

        is_sponsored = any(k in url for k in ['sponsored', 'ad', 'utm_source=ad', 'track', 'promo', 'ref'])
        is_video = any(k in url for k in ['youtube.com', 'vimeo.com', '.mp4', 'video'])
        is_organic = not is_sponsored
        is_article = not is_video

        cursor.execute('''
            INSERT INTO results_table (
                search_id, url_link, isVideo, isArticle, isOrganic, isSponsored
            ) VALUES (%s, %s, %s, %s, %s, %s)
        ''', (search_id, url, is_video, is_article, is_organic, is_sponsored))
        inserted_count += 1
    return inserted_count

def run_search(search_term, engine, num_results, search_id):
    import mysql.connector

    #print(f" Running search: '{search_term}' on {engine}, retrieving up to {num_results} results")

    urls = get_urls(search_term, engine, num_results)

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="MY_CUSTOM_BOT",
        use_unicode=True,
        charset="utf8mb4"
    )
    cursor = connection.cursor(dictionary=True)

    inserted_count = urls_to_results_table(search_id, urls, cursor)
    connection.commit()
    connection.close()

    # msg = f"Retrieving {'all available' if not num_results else f'{num_results}'} results"
    # print(f" Running search: '{search_term}' on {engine} — {msg}")
    # print(f"Inserted {inserted_count} URLs into results_table for search_id={search_id}")