import json
import torch
from rabbitMQ.services.api_client import send_to_api_async
from config import API_ENDPOINTS

def map_emotion_label(class_id):
    # Map 5-class sentiment to 7 standard emotions
    # 0: Very negative -> angry
    # 1: Negative      -> sad
    # 2: Neutral       -> neutral
    # 3: Positive      -> happy
    # 4: Very positive -> surprise
    mapping = {
        0: "angry",
        1: "sad",
        2: "neutral",
        3: "happy",
        4: "surprise"
    }
    # Support both int and str keys
    if isinstance(class_id, str) and class_id.isdigit():
        class_id = int(class_id)
    return mapping.get(class_id, "neutral")

def create_text_callback(model, tokenizer, id2label):
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
    return callback_txt
