import streamlit as st
import subprocess
import pandas as pd
import mysql.connector
from datetime import datetime
import urllib.parse

# === Streamlit App Layout ===
st.set_page_config(page_title="Web Search Engine", layout="wide")
st.title("🔍 Web Content Search Engine")

# === Inputs in a single row ===
col1, col2 = st.columns([4, 1])
with col1:
    search_term = st.text_input("Enter your search term:")
with col2:
    engine = st.selectbox("Choose a search engine:", ["Google", "Bing", "Yahoo", "DuckDuckGo"])

N_cards_per_row = 3

# === Run search automatically when term is entered ===
if search_term:
    start_time = datetime.now()
    st.info("📡 Searching ...")

    process = subprocess.run(
        ["python", "main.py", search_term, engine],
        capture_output=True,
        text=True
    )

    if process.returncode != 0:
        st.error("❌ Pipeline failed.")
        st.text(process.stderr)
    else:
        st.success("✅ Pipeline completed.")
        st.text(f"Time taken: {datetime.now() - start_time}")

        # === Get the latest search_id ===
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="",
                database="MY_CUSTOM_BOT",
                use_unicode=True,
                charset="utf8mb4"
            )
            cursor = connection.cursor()
            cursor.execute('''
                SELECT MAX(search_id) 
                FROM search_table 
                WHERE search_term = %s
            ''', (search_term.lower(),))
            search_id = cursor.fetchone()[0]
            connection.close()
        except Exception as e:
            st.error("Failed to retrieve search_id.")
            st.text(str(e))
            search_id = None

        # === Fetch results and display as cards ===
        if search_id:
            try:
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
                    SELECT DISTINCT tf.search_term, tf.url, tf.frequency, ci.title, ci.content_details
                    FROM term_frequency tf
                    JOIN content_info ci ON tf.url = ci.url AND tf.search_id = ci.search_id
                    WHERE tf.search_id = %s
                    ORDER BY tf.frequency DESC
                ''', (search_id,))

                results = cursor.fetchall()
                connection.close()

                if not results:
                    st.warning("No results found for this search term.")
                else:
                    df = pd.DataFrame(results)
                    st.markdown("### 🔗 Ranked Results")

                    for i, row in df.iterrows():
                        if i % N_cards_per_row == 0:
                            if i > 0:
                                st.markdown('<div style="margin-top: 25px;"></div>', unsafe_allow_html=True)
                            cols = st.columns(N_cards_per_row, gap="large")

                        domain = urllib.parse.urlparse(row['url']).netloc.replace("www.", "")
                        favicon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"
                        snippet = row['content_details'][:200].replace('\n', ' ') if row['content_details'] else ''
                        title = row['title'] if row['title'] else domain

                        with cols[i % N_cards_per_row]:
                            st.markdown(f"""
                                <a href="{row['url']}" target="_blank" style="text-decoration: none;">
                                    <div style="
                                        border: 1px solid #e1e4e8;
                                        border-radius: 8px;
                                        padding: 12px;
                                        margin-bottom: 12px;
                                        box-shadow: 1px 1px 6px rgba(0, 0, 0, 0.05);
                                        transition: 0.3s all ease-in-out;
                                        background-color: white;
                                    ">
                                        <img src="{favicon_url}" width="20" style="vertical-align:middle; margin-right:6px;">
                                        <strong style="font-size:16px;">{title}</strong><br>
                                        <small style="color:#444;">{row['url']}</small><br>
                                        <small style="color:#666;">Matched term: <em>{row['search_term']}</em></small>
                                        <p style="font-size:13px; color:#444; margin-top:6px;">
                                            {snippet}...
                                        </p>
                                        <div style="margin-top: 8px;">
                                            <span style="
                                                background-color: #eef2f6;
                                                color: #1a1a1a;
                                                padding: 3px 8px;
                                                font-size: 12px;
                                                border-radius: 12px;
                                                display: inline-block;
                                            ">
                                                📊 {row["frequency"]} matches
                                            </span>
                                        </div>
                                    </div>
                                </a>
                            """, unsafe_allow_html=True)

            except Exception as e:
                st.error("Error retrieving or displaying results.")
                st.text(str(e))
