# 🔎 Multi-Engine Search Pipeline with OCR & SQL Storage

A custom-built data engineering pipeline that scrapes search results from Google, Bing, and Yahoo, captures and extracts text using OCR (Tesseract), stores the results in a MySQL database, and displays relevant term-frequency matches through a Streamlit web app.

--- 

## 🚀 Project Overview
This project simulates a full-scale data ingestion and processing workflow. It automates the following:
1. **Search Query Execution** - Uses web scraping to collect results from major search engines.
2. **Screenshot Capture** - Saves result previews as images.
3. **OCR Processing** - Applies Tesseract to extract text from screenshots.
4. **SQL Storage** - Cleans and stores structured content in a MySQL database.
5. **Search Term Matching** - Calculates keyword frequency from extracted content.
6. **Interactive Front-End** - Displays results in a user-friendly Streamlit interface.

--- 

## 📁 Tech Stack
- **Languages:** Python
- **Libraries:** BeautifulSoup, Requests, Tesseract OCR, pdf2image, Streamlit, pandas, mysql-connector-python
- **Database:** MySQL
- **UI:** Streamlit

---

## 🧱 Project Architecture
```bash
main.py                                        # Entry point
search_engine.py                               # Queries search engines and collects URLs
screenshot.py                                  # Captures webpage screenshots
ocr.py                                         # Extracts text from screenshots (via Tesseract)
db.py                                          # Handles MySQL connections and term frequency storage
app.py                                         # Streamlit interface to display results
```

🧪 How It Works
1. Input: User types a keyword, chooses a search engine, and sets the number of results.
2. Pipeline:
  - Scrape URLs -> Capture screenshot -> OCR -> Clean text
  - Store all extracted content in MySQL (content_info table)
3. Analysis:
  - Compute keyword frequency for each result
  - Display top matches with titles, URLs, and frequency scores
4. Output: A Streamlit dashboard for keyword exploration using hover tooltips and filters.

🌐[Live App on Streamlit](https://data-engineering-final.streamlit.app/)


📝 Lessons Learned
- Built a modular ETL pipeline from scratch with real-time scraping
- Managed local OCR workflows using Tesseract and pdf2image
- Designed normalized SQL schemas for storing semi-structured data
- Streamlined data exploration through a custom front-end dashboard


📧 Contact:
Feel free to connect with me on [LinkedIn](https://www.linkedin.com/in/tyleranatole/) or reach out if you're interested in how this project was built!
  
