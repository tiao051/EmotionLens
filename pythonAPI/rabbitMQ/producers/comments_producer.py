import json
import pika
from rabbitMQ.connection.connection import get_rabbitmq_connection

class CommentQueueProducer:
    def __init__(self, queue_name="comments_queue"):
        self.queue_name = queue_name
        self.connection = get_rabbitmq_connection()
        if self.connection is None:
            raise RuntimeError(f"❌ Failed to connect to RabbitMQ {queue_name}.")
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def send_comment_to_queue(self, text, author, video_id, is_final):
        message = {
            "Text": text,
            "author": author,
            "video_id": video_id,
            "is_final": is_final
        }
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        print(f"📤 Sent comment by '{author}' to queue: {self.queue_name}")

    def close(self):
        if self.connection:
            self.connection.close()
            print(f"✅ Closed connection to RabbitMQ {self.queue_name}.")
