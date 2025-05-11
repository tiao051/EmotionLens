import json
from rabbitMQ.services.api_client import send_to_api_async
from config import API_ENDPOINTS

async def callback_txt(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    text_content = message.get("Text")

    print(f"Received ID: {file_id}")
    print(f"Received text content: {text_content}")

    try:
        emotion_result = "Happy" 

        print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

        result_message = {
            "Id": file_id,
            "Emotion": emotion_result
        }
        print(f"Data sent to C#: {result_message}")

        await send_to_api_async(result_message, API_ENDPOINTS["text"])

    except Exception as e:
        print(f"Error processing text with ID {file_id}: {e}")


    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Text with ID: {file_id} processed and acknowledged.")