import pika
import time
import threading

def get_rabbitmq_connection():
    print("cc j v")
    connection_event = threading.Event()
    connection = None

    def connect():
        nonlocal connection
        while True:
            try:    
                print("123")
                connection = pika.BlockingConnection(pika.ConnectionParameters(
                    host='localhost',
                    port=5672,
                    credentials=pika.PlainCredentials('admin', 'admin')
                ))
                print("Connection to RabbitMQ successful")
                connection_event.set()  # Đánh dấu kết nối thành công
                break
            except pika.exceptions.AMQPConnectionError as e:
                print(f"Failed to connect to RabbitMQ: {e}. Retrying in 5 seconds...")
                time.sleep(5)

    # Chạy connect trong một thread riêng
    connection_thread = threading.Thread(target=connect)
    connection_thread.start()

    # Chờ đến khi kết nối thành công
    connection_event.wait()

    if connection is None:
        print("Connection to RabbitMQ failed after several attempts.")
    return connection
