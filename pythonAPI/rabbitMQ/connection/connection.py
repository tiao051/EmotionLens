import pika
import threading
import time
from config import RABBITMQ_CONFIG

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
                    ),
                    heartbeat=600,
                    blocked_connection_timeout=300,
                ))
                print("✅ Connected to RabbitMQ")
                connection_event.set()
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"❌ RabbitMQ Connection Failed: {e}. Retrying in 5s...")
                time.sleep(5)

    threading.Thread(target=connect).start()
    connection_event.wait()
    return connection
