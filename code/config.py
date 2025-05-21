import os
from datetime import datetime

azure_subscription_key = "hfaVoY37mnYYtJDsxyvULLxFxlAmgpLuC9KlnELvov8fIA7l30htJQQJ99BEACYeBjFXJ3w3AAAFACOGHITp"
azure_endpoint = "https://data-engineering-project.cognitiveservices.azure.com/"

screenshot_folder = "screenshots"
os.makedirs(screenshot_folder, exist_ok=True)

tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'