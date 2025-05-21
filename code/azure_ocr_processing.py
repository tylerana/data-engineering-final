# def ocr_processing(search_id):
#     import time
#     import mysql.connector
#     from mysql.connector import connect
#     from config import azure_subscription_key, azure_endpoint
#     from azure.cognitiveservices.vision.computervision import ComputerVisionClient
#     from msrest.authentication import CognitiveServicesCredentials

#     connection = connect(
#         host="localhost",
#         user="root",
#         password="",
#         database="MY_CUSTOM_BOT"
#     )
#     cursor = connection.cursor(dictionary=True)

#     client = ComputerVisionClient(
#         azure_endpoint,
#         CognitiveServicesCredentials(azure_subscription_key)
#     )


#     cursor.execute('''
#         SELECT search_id, url, media_id, media_type
#         FROM media_output
#         WHERE search_id = %s
#     ''', (search_id,))
#     rows = cursor.fetchall()

#     inserted_count = 0
#     skipped = 0
#     failed = 0

#     unsupported_types = ["zip", "mp4", "mp3", "webm", "exe", "json"]

#     for row in rows:
#         url = row['url']
#         media_type = row.get('media_type', '').lower()

#         if media_type in unsupported_types:
#             print(f"Skipping unsupported type: {media_type} for {url}")
#             skipped += 1
#             continue

#         try:
#             read_response = client.read(url, raw=True)
#             read_operation_location = read_response.headers["Operation-Location"]
#             operation_id = read_operation_location.split("/")[-1]

#             # Poll for result
#             while True:
#                 result = client.get_read_result(operation_id)
#                 if result.status in ["succeeded", "failed"]:
#                     break
#                 time.sleep(1)

#             if result.status == "succeeded":
#                 lines = []
#                 for page in result.analyze_result.read_results:
#                     for line in page.lines:
#                         lines.append(line.text)
#                 ocr_text = "\n".join(lines)

#                 if ocr_text.strip():
#                     cursor.execute('''
#                         INSERT INTO content_info (search_id, url, info_type, content_details)
#                         VALUES (%s, %s, 'ocr_text', %s)
#                     ''', (search_id, url, ocr_text.strip().lower()))
#                     inserted_count += 1
#                 else:
#                     print(f" No text found in {url}")
#                     failed += 1
#             else:
#                 print(f"Azure OCR failed for {url}")
#                 failed += 1

#         except Exception as e:
#             print(f"Exception during OCR for {url}: {e}")
#             failed += 1
#             continue

#     connection.commit()
#     cursor.close()
#     connection.close()

#     print(f" Azure OCR done: {inserted_count} inserted, {skipped} skipped, {failed} failed.")
