import json
import os
from pathlib import Path
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

from rabbitMQ.services.api_client import send_to_api_async
from config import API_ENDPOINTS

# Biến toàn cục để lưu model/tokenizer/id2label
model = None
tokenizer = None
id2label = None

def load_text_model():
    global model, tokenizer, id2label
    # Đường dẫn tuyệt đối tới best_model
    MODEL_DIR = Path(__file__).resolve().parent.parent.parent / 'emotion_model' / 'text_model' / 'best_model'
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
    tokenizer = DistilBertTokenizer.from_pretrained(MODEL_DIR)
    model.eval()
    id2label = model.config.id2label
    print(f"Text model loaded successfully from {MODEL_DIR}.")

def map_emotion_label(class_id):
    mapping = {
        0: "Very negative",
        1: "Negative",
        2: "Neutral",
        3: "Positive",
        4: "Very positive"
    }
    # Hỗ trợ cả int và str key
    if isinstance(class_id, str) and class_id.isdigit():
        class_id = int(class_id)
    return mapping.get(class_id, str(class_id))

async def callback_txt(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    text_content = message.get("Text")

    print(f"Received ID: {file_id}")
    print(f"Received text content: {text_content}")

    try:
        # Tokenize văn bản
        inputs = tokenizer(text_content, return_tensors="pt", truncation=True, padding=True, max_length=128)

        # Dự đoán
        with torch.no_grad():
            outputs = model(**inputs)
            predicted_class_id = torch.argmax(outputs.logits, dim=1).item()
            # Map kết quả ra chữ
            predicted_label = map_emotion_label(predicted_class_id)

        print(f"Emotion analysis result for ID {file_id}: {predicted_label}")

        result_message = {
            "Id": file_id,
            "Emotion": predicted_label
        }

        print(f"Data sent to C#: {result_message}")
        await send_to_api_async(result_message, API_ENDPOINTS["text"])

    except Exception as e:
        print(f"Error processing text with ID {file_id}: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Text with ID: {file_id} processed and acknowledged.")
