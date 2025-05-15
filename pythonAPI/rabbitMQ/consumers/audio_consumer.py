import json
from rabbitMQ.services.api_client import send_to_api_async
from config import API_ENDPOINTS

def create_audio_callback(model):
    async def callback_audio(ch, method, properties, body):
        message = json.loads(body)
        file_id = message.get("Id")
        file_path = message.get("FilePath")

        print(f"Received ID: {file_id}")
        print(f"Received audio content: {file_path}")

        # xử lý model
        try:
            emotion_result = "Happy"  

            print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

            result_message = {
                "Id": file_id,
                "Emotion": emotion_result
            }
            print(f"Data sent to C#: {result_message}")

            await send_to_api_async(result_message, API_ENDPOINTS["audio"])

        except Exception as e:
            print(f"Error processing text with ID {file_id}: {e}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Audio with ID: {file_id} processed and acknowledged.")
    return callback_audio