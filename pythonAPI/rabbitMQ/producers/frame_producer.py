import os
import json
import pika
from rabbitMQ.connection.connection import get_rabbitmq_connection

class FrameQueueProducer:
    def __init__(self, queue_name="fps_queue"):
        self.queue_name = queue_name
        self.connection = get_rabbitmq_connection()
        if self.connection is None:
            raise RuntimeError(f"❌ Failed to connect to RabbitMQ {queue_name}.")
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def send_frame_to_queue(self, frame_path, video_id, is_final):
        message = {
            "Id": os.path.basename(frame_path),
            "FilePath": frame_path,
            "video_id": video_id,
            "is_final": is_final
        }
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,
            )
        )
        print(f"Sent frame: {frame_path} to queue: {self.queue_name}")

    def close(self):
        if self.connection:
            self.connection.close()
            print(f"✅ Closed connection to RabbitMQ {self.queue_name}.")
