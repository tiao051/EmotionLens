import pika
import json
import os
from rabbitMQ.connection.connection import get_rabbitmq_connection

class TextQueueProducer:
    def __init__(self, queue_name="comments_queue"):
        self.queue_name = queue_name
        self.connection = get_rabbitmq_connection()
        if self.connection is None:
            raise RuntimeError(f"❌ Failed to connect to RabbitMQ {queue_name}.")
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def send_comment_to_queue(self, message: dict):
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            )
        )
        print(f"📤 Sent comment by '{message.get('author', 'unknown')}' to queue '{self.queue_name}'")

    def close(self):
        self.connection.close()
