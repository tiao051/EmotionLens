import os
from dotenv import load_dotenv

load_dotenv()
RABBITMQ_CONFIG = {
    "host": "localhost",
    "port": 5672,
    "username": "test1",
    "password": os.getenv('RABBITMQ_PASSWORD')
}

API_ENDPOINTS = {
    "image": "https://localhost:44354/api/DataReceive/data-img",
    "text": "https://localhost:44354/api/DataReceive/data-text",
    "audio": "https://localhost:44354/api/DataReceive/data-audio",
    "tiktok": "https://localhost:44354/api/DataReceive/data-tiktok"
}

TIKTOK_API_CONFIG = {
    "ms_token": os.getenv('TIKTOK_MS_TOKEN'),
    "save_csv_path": "D:\\Deep_Learning\\dataSet\\exportData\\tiktokExport"
}

# MODEL_NAME = "VGG-Face"