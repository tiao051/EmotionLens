import os
from dotenv import load_dotenv

load_dotenv()
RABBITMQ_CONFIG = {
    "host": "localhost",
    "port": 5672,
    "username": "admin",
    "password": os.getenv('RABBITMQ_PASSWORD')
}

API_ENDPOINTS = {
    "image": "https://localhost:44354/api/SingleDataReceive/single-data-img",
    "text": "https://localhost:44354/api/SingleDataReceive/single-data-text",
    "audio": "https://localhost:44354/api/SingleDataReceive/single-data-audio",
    "multi_image": "https://localhost:44354/api/MultiDataReceive/multi-data-img",
    "multi_text": "https://localhost:44354/api/MultiDataReceive/multi-data-text",
    "multi_audio": "https://localhost:44354/api/MultiDataReceive/multi-data-audio"
}

TIKTOK_API_CONFIG = {
    "ms_token": os.getenv('TIKTOK_MS_TOKEN'),
    "save_csv_path": "D:\\Deep_Learning\\dataSet\\exportData\\pythonExportData\\tiktok_cmt_data"
}