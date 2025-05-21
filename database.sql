DROP DATABASE IF EXISTS MY_CUSTOM_BOT; 
CREATE DATABASE MY_CUSTOM_BOT;
SHOW DATABASES;
USE MY_CUSTOM_BOT;

CREATE TABLE search_table (
search_id INT AUTO_INCREMENT PRIMARY KEY,
search_term VARCHAR(256),
search_engine VARCHAR(25),
num_results INT,
search_date DATETIME, 
search_time FLOAT
);

CREATE TABLE results_table (
results_id INT AUTO_INCREMENT PRIMARY KEY,
search_id INT,
url_link TEXT,
results_title TEXT, 
results_summary TEXT,
isVideo BOOL, 
isArticle BOOL, 
isOrganic BOOL, 
isSponsored BOOL,
FOREIGN KEY (search_id) REFERENCES search_table(search_id)
);

CREATE TABLE ocr_screenshots (
  ocr_id INT AUTO_INCREMENT PRIMARY KEY,
  search_id INT,
  screenshot_path TEXT,
  ocr_data TEXT,
  FOREIGN KEY (search_id) REFERENCES search_table(search_id)
);

CREATE TABLE scripts_table (
  script_id INT AUTO_INCREMENT PRIMARY KEY,
  script_name VARCHAR(100),
  run_timestamp DATETIME
);

-- the purpose of this table is to store information from the urls we store from the results_table
CREATE TABLE scrape_info (
scrape_id INT AUTO_INCREMENT PRIMARY KEY,
search_id INT,
url TEXT,
cleaned_text TEXT,
FOREIGN KEY(search_id) REFERENCES search_table(search_id)
);

CREATE TABLE term_frequency(
term_id INT AUTO_INCREMENT PRIMARY KEY,
search_id INT, 
search_term VARCHAR(255),
url TEXT, 
frequency INT,
FOREIGN KEY(search_id) REFERENCES search_table(search_id)
);

CREATE TABLE media_output (
media_id INT AUTO_INCREMENT PRIMARY KEY,
search_id INT,
url TEXT,
media_url TEXT,
media_type TEXT,
FOREIGN KEY(search_id) REFERENCES search_table(search_id)
);

CREATE TABLE content_info (
content_id INT AUTO_INCREMENT PRIMARY KEY, 
search_id INT, 
url TEXT,
info_type VARCHAR(100),
content_details LONGTEXT,
title TEXT,
FOREIGN KEY (search_id) REFERENCES search_table(search_id)
);


-- -------------------------------------------------------------------------------------------------
DESCRIBE content_info;
ALTER TABLE content_info ADD COLUMN title TEXT;

SELECT results_title, results_summary FROM results_table ORDER BY results_id DESC LIMIT 15;
SELECT * FROM search_table;
SELECT * FROM scripts_table;
SELECT * FROM ocr_screenshots;
SELECT * FROM results_table;
SELECT * from content_info;
SHOW CREATE TABLE content_info;
SELECT * from term_frequency;

-- changing text to longtext
ALTER TABLE content_info
MODIFY content_details LONGTEXT
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;


SELECT search_id, url, COUNT(*)
	FROM content_info
	WHERE info_type IN ('text', 'ocr_text')
	GROUP BY search_id, url
	HAVING COUNT(*) > 1;
    
SELECT info_type, COUNT(*) FROM content_info GROUP BY info_type;
SELECT media_type, COUNT(*) FROM media_output GROUP BY media_type;
SELECT * FROM term_frequency ORDER BY frequency DESC LIMIT 10;
SELECT * FROM search_table ORDER BY search_id DESC LIMIT 1;
SELECT * FROM content_info;

SELECT * FROM term_frequency WHERE search_term = "pediatric leukemia morbidity rate";

SELECT info_type, COUNT(*) 
FROM content_info 
WHERE search_id = 14 
GROUP BY info_type;

SELECT LENGTH(content_details) AS len, info_type 
FROM content_info 
WHERE search_id = 14 
ORDER BY len DESC 
LIMIT 5;

SELECT content_details
FROM content_info
WHERE search_id = 14
AND content_details LIKE '%pediatric leukemia morbidity rate%'
LIMIT 1;

SELECT COUNT(*) 
FROM content_info 
WHERE search_id = 16 
AND LOWER(content_details) LIKE '%pediatric%leukemia%morbidity%rate%';
