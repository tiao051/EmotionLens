import json
import pika
import threading
import aiohttp
import time
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from emotion_model.deepfaceAPI.deepfacemodel import load_or_download_model, analyze_image_emotion
from config import RABBITMQ_CONFIG, API_ENDPOINTS, MODEL_NAME
# from consumer_utils import send_result_to_api

def get_rabbitmq_connection():
    connection_event = threading.Event()
    connection = None

    def connect():
        nonlocal connection
        while True:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host=RABBITMQ_CONFIG["host"],
                    port=RABBITMQ_CONFIG["port"],
                    credentials=pika.PlainCredentials(
                        RABBITMQ_CONFIG["username"],
                        RABBITMQ_CONFIG["password"]
                    )
                ))
                print("✅ Connected to RabbitMQ (consumer)")
                connection_event.set()
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"❌ Failed to connect to RabbitMQ: {e}. Retrying in 5 seconds...")
                time.sleep(5)
    connection_thread = threading.Thread(target=connect)
    connection_thread.start()
    connection_event.wait()
    return connection

def callback_url(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    file_path = message.get("FilePath")
    
    print(f"Received ID: {file_id}")
    print(f"Received file path: {file_path}")
    # xử lý file tại đây...
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"File with ID: {file_id} processed and acknowledged.")

async def callback_img(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    file_path = message.get("FilePath")

    print(f"Received ID: {file_id}")
    print(f"Received image path: {file_path}")

    try:
        # Load the DeepFace model
        model = load_or_download_model(MODEL_NAME)

        if model:
            emotion_result = analyze_image_emotion(file_path, model)

            print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

            result_message = {
                "Id": file_id,
                "Emotion": emotion_result
            }
            print(f"Data sent to C#: {result_message}")

            await send_to_api_async(result_message, API_ENDPOINTS["image"])
            
        else:
            print("Failed to load the DeepFace model.")

    except Exception as e:
        print(f"Error processing image with ID {file_id}: {e}")

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Image with ID: {file_id} processed and acknowledged.")
    
async def callback_txt(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    text_content = message.get("TextContent")

    print(f"Received ID: {file_id}")
    print(f"Received text content: {text_content}")

    try:
        emotion_result = "Happy"  # Hardcoded result for testing

        print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

        result_message = {
            "Id": file_id,
            "Emotion": emotion_result
        }
        print(f"Data sent to C#: {result_message}")

        await send_to_api_async(result_message, API_ENDPOINTS["text"])

    except Exception as e:
        print(f"Error processing text with ID {file_id}: {e}")

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Text with ID: {file_id} processed and acknowledged.")

async def callback_audio(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    text_content = message.get("AudioContent")

    print(f"Received ID: {file_id}")
    print(f"Received audio content: {text_content}")

    try:
        emotion_result = "Happy"  # Hardcoded result for testing

        print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

        result_message = {
            "Id": file_id,
            "Emotion": emotion_result
        }
        print(f"Data sent to C#: {result_message}")

        await send_to_api_async(result_message, API_ENDPOINTS["audio"])

    except Exception as e:
        print(f"Error processing text with ID {file_id}: {e}")

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Audio with ID: {file_id} processed and acknowledged.")

async def callback_tiktok(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    url_content = message.get("UrlContent")

    print(f"Received ID: {file_id}")
    print(f"Received tiktok url content: {url_content}")
    
    try:
        emotion_result = "Happy"  # Hardcoded result for testing

        print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

        result_message = {
            "Id": file_id,
            "Emotion": emotion_result
        }
        print(f"Data sent to C#: {result_message}")

        await send_to_api_async(result_message, API_ENDPOINTS["tiktok"])

    except Exception as e:
        print(f"Error processing text with ID {file_id}: {e}")

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Tiktok URL with ID: {file_id} processed and acknowledged.")
    
def start_consumer(queue_name, callback):
    print(f"🚀 Starting RabbitMQ consumer for {queue_name}...")
    connection = get_rabbitmq_connection()
    if connection is None:
        print(f"❌ Failed to connect to RabbitMQ {queue_name}.")
        return

    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

    print(f"⏳ Waiting for messages in {queue_name}.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"🛑 Stopping {queue_name} consumer...")
        channel.stop_consuming()
    finally:
        connection.close()
        print(f"✅ Closed connection to RabbitMQ {queue_name}.")
        
async def send_to_api_async(data, api_url):
    headers = {"Content-Type": "application/json"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(api_url, json=data, headers=headers, ssl=False) as response:
                if response.status == 200:
                    print(f"Successfully sent data to C#: {response.status}, {await response.text()}")
                else:
                    print(f"Failed to send data to C#: {response.status}, {await response.text()}")
        except Exception as e:
            print(f"Error sending data to C#: {e}")
        