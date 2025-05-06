import json
import pika
import threading
import time
import numpy as np
from emotion_model.deepfaceAPI.deepfacemodel import load_or_download_model, analyze_image_emotion
from rabbitMQ.producer import send_result_to_rabbitmq

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
                    credentials=pika.PlainCredentials('admin', 'admin')
                ))
                print("✅ Connected to RabbitMQ")
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
            # Analyze the emotion from the image
            emotion_result = analyze_image_emotion(file_path, model)

            print(f"Emotion analysis result for ID {file_id}: {emotion_result}")
            
            result_message = {
                "Id": file_id,
                "Emotion": emotion_result
            }
            
            print(f"Result message: {result_message}")
            send_result_to_rabbitmq(result_message)
        else:
            print("Failed to load the DeepFace model.")

    except Exception as e:
        print(f"Error processing image with ID {file_id}: {e}")

    # Acknowledge the message
    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Image with ID: {file_id} processed and acknowledged.")
    
def start_rabbitmq_consumer():
    print("🚀 Starting RabbitMQ consumer for url...")
    connection = get_rabbitmq_connection()
    if connection is None:
        print("❌ Failed to connect to RabbitMQ.")
        return

    channel = connection.channel()

    # Đảm bảo queue tồn tại
    channel.queue_declare(queue='excel_queue', durable=True)

    # auto_ack=False để chủ động xử lý ack
    channel.basic_consume(queue='excel_queue', on_message_callback=callback, auto_ack=False)

    print("⏳ Waiting for messages. Press CTRL+C to exit.")
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
        print("❌ Failed to connect to RabbitMQ.")
        return

    channel = connection.channel()

    # Đảm bảo queue tồn tại
    channel.queue_declare(queue='img_queue', durable=True)

    # auto_ack=False để chủ động xử lý ack
    channel.basic_consume(queue='img_queue', on_message_callback=callback_img, auto_ack=False)

    print("⏳ Waiting for messages in img_queue. Press CTRL+C to exit.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("🛑 Stopping img_queue consumer...")
        channel.stop_consuming()
    finally:
        connection.close()
