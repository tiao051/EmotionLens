import json
import pika
from rabbitMQ.connection.connection import get_rabbitmq_connection

class AudioSectionProducer:
    def __init__(self, queue_name="audio_sections_queue"):
        self.queue_name = queue_name
        self.connection = get_rabbitmq_connection()
        if self.connection is None:
            raise RuntimeError(f"❌ Failed to connect to RabbitMQ {queue_name}.")
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=True)

    def send_section_path(self, file_path, video_id, section_index):
        message = {
            "FilePath": file_path,
            "Id": video_id,
            "section_index": section_index
        }
        self.channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  
            )
        )
        print(f"📤 Sent section {section_index} of video '{video_id}' to queue.")

    def close(self):
        if self.connection:
            self.connection.close()
            print(f"✅ Closed connection to RabbitMQ {self.queue_name}.")
