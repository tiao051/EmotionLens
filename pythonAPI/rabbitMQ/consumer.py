import json
import pika
import threading
import time
import numpy as np
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from emotion_model.deepfaceAPI.deepfacemodel import load_or_download_model, analyze_image_emotion

def get_rabbitmq_connection():
    connection_event = threading.Event()
    connection = None

    def connect():
        nonlocal connection
        while True:
            try:
                connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host='localhost',
                    port=5672,
                    credentials=pika.PlainCredentials('test1', 'test1')
                ))
                print("✅ Connected to RabbitMQ (consumer)")
                connection_event.set()
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"❌ Failed to connect to RabbitMQ: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    connection_thread = threading.Thread(target=connect)
    connection_thread.start()
    threading.Thread(target=connect).start()
    connection_event.wait()
    return connection

def callback(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    file_path = message.get("FilePath")
    
    print(f"Received ID: {file_id}")
    print(f"Received file path: {file_path}")
    # xử lý file tại đây...
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"File with ID: {file_id} processed and acknowledged.")

def callback_img(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    file_path = message.get("FilePath")

    print(f"Received ID: {file_id}")
    print(f"Received image path: {file_path}")

    try:
        # Load the DeepFace model
        model_name = "VGG-Face"
        model = load_or_download_model(model_name)

        if model:
            emotion_result = analyze_image_emotion(file_path, model)

            print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

            result_message = {
                "Id": file_id,
                "Emotion": emotion_result
            }
            print(f"Data sent to C#: {result_message}")

            url = "https://localhost:44354/api/DataReceive/data-img" 
            headers = {"Content-Type": "application/json"}

            try:
                response = requests.post(url, json=result_message, headers=headers, verify=False)
                print(f"Response from C#: {response.status_code}, {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"Error sending data to C#: {e}")
        else:
            print("Failed to load the DeepFace model.")

    except Exception as e:
        print(f"Error processing image with ID {file_id}: {e}")

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Image with ID: {file_id} processed and acknowledged.")
    
def call_back_txt(ch, method, properties, body):
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

        url = "https://localhost:44354/api/DataReceive/data-text" 
        headers = {"Content-Type": "application/json"}

        try:
            response = requests.post(url, json=result_message, headers=headers, verify=False)
            print(f"Response from C#: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending data to C#: {e}")

    except Exception as e:
        print(f"Error processing text with ID {file_id}: {e}")

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Text with ID: {file_id} processed and acknowledged.")

def start_url_rabbitmq_consumer():
    print("🚀 Starting RabbitMQ consumer for url...")
    connection = get_rabbitmq_connection()
    if connection is None:
        print("❌ Failed to connect to RabbitMQ Url.")
        return

    channel = connection.channel()
    channel.queue_declare(queue='excel_queue', durable=True)
    channel.basic_consume(queue='excel_queue', on_message_callback=callback, auto_ack=False)

    print("⏳ Waiting for messages in txt queue. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("🛑 Stopping consumer...")
        channel.stop_consuming()
    finally:
        connection.close()

def start_img_queue_consumer():
    print("🚀 Starting RabbitMQ consumer for img_queue...")
    connection = get_rabbitmq_connection()
    if connection is None:
        print("❌ Failed to connect to RabbitMQ Img.")
        return

    channel = connection.channel()
    channel.queue_declare(queue='img_queue', durable=True)
    channel.basic_consume(queue='img_queue', on_message_callback=callback_img, auto_ack=False)

    print("⏳ Waiting for messages in img_queue. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("🛑 Stopping img_queue consumer...")
        channel.stop_consuming()
    finally:
        connection.close()

def start_txt_rabbitmq_consumer():
    print("🚀 Starting RabbitMQ consumer for txt_queue...")
    connection = get_rabbitmq_connection()
    if connection is None:
        print("❌ Failed to connect to RabbitMQ TxT.")
        return

    channel = connection.channel()
    channel.queue_declare(queue='txt_queue', durable=True)
    channel.basic_consume(queue='txt_queue', on_message_callback=call_back_txt, auto_ack=False)

    print("⏳ Waiting for messages in txt_queue. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("🛑 Stopping txt_queue consumer...")
        channel.stop_consuming()
    finally:
        connection.close()