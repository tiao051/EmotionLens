import json
import pika
import threading
import time

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

def start_rabbitmq_consumer():
    print("🚀 Starting RabbitMQ consumer...")
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
