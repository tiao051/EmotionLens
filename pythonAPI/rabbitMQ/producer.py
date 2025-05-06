import pika
import json

def send_result_to_rabbitmq(result, queue_name="emotion_img_result_queue"):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=queue_name, durable=True)

    message = json.dumps(result)
    channel.basic_publish(
        exchange='',
        routing_key=queue_name,
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,  # make message persistent
        )
    )
    connection.close()
    print(f"Sent result to RabbitMQ queue '{queue_name}': {message}")