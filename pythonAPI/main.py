import threading
import asyncio
from tensorflow.keras.models import load_model as keras_load_model # type: ignore
from emotion_model.deepfaceAPI.deepfacemodel import load_deepface_model
from tensorflow.keras.models import load_model # type: ignore
from rabbitMQ.connection.connection import get_rabbitmq_connection
from emotion_model.efficientNet_model.build import build_finetune_efficientnet

from rabbitMQ.consumers import (
    audio_consumer,
    image_consumer,
    tiktok_consumer,
    text_consumer,
    url_consumer,
)

# AUDIO_MODEL_PATH = r"D:\Deep_Learning\main\pythonAPI\emotion_model\audio_model\audio_model.h5"
# audio_model = keras_load_model(AUDIO_MODEL_PATH)

def train_all_models():
    from emotion_model.img_model.train import train_img_emotion_model
    from emotion_model.efficientNet_model.train import train_efficientnet_emotion_model
    
    train_img_emotion_model()
    train_efficientnet_emotion_model()

def load_all_models():
    # load_deepface_model()
    text_consumer.load_text_model()
    # model = load_model('D:/Deep_Learning/main/pythonAPI/emotion_model/efficientNet_model/efficientnet_emotion_model')
    pass

def start_consumer(queue_name, callback):
    connection = get_rabbitmq_connection()
    if connection is None:
        print(f"❌ Failed to connect to RabbitMQ {queue_name}.")
        return

    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

    print(f"⏳ Waiting for messages in {queue_name}.")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"🛑 Stopping {queue_name} consumer...")
        channel.stop_consuming()
    finally:
        connection.close()
        print(f"✅ Closed connection to RabbitMQ {queue_name}.")
        
def start_all_consumers():
    # Build EfficientNet model ONCE and create callback for image queue
    efficientnet_model = build_finetune_efficientnet(input_shape=(48, 48, 3), num_classes=7)
    img_callback = image_consumer.create_img_callback(efficientnet_model)
    
    # model = load_model('D:/Deep_Learning/main/pythonAPI/emotion_model/efficientNet_model/efficientnet_emotion_model')
    # img_callback = image_consumer.create_img_callback(model)
    consumers = [
        {"queue": "txt_queue", "callback": lambda ch, m, p, b: asyncio.run(text_consumer.callback_txt(ch, m, p, b))},
        # {"queue": "audio_queue", "callback": lambda ch, m, p, b: asyncio.run(audio_consumer.create_audio_callback(audio_model)(ch, m, p, b))},
        {"queue": "img_queue", "callback": lambda ch, m, p, b: asyncio.run(img_callback(ch, m, p, b))},
        {"queue": "tiktok_queue", "callback": lambda ch, m, p, b: asyncio.run(tiktok_consumer.process_tiktok_callbacks(ch, m, p, b))},
        {"queue": "csv_queue", "callback": url_consumer.callback_url}
    ]

    threads = []
    for c in consumers:
        thread = threading.Thread(target=start_consumer, args=(c["queue"], c["callback"]))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

if __name__ == "__main__":
    print("🎯 Starting all Rab  bitMQ consumers and model loading...")

    # Chạy load_all_models song song với consumers
    load_thread = threading.Thread(target=load_all_models)
    consumers_thread = threading.Thread(target=start_all_consumers)
    # train_all_models_thread = threading.Thread(target=train_all_models)

    load_thread.start()
    consumers_thread.start()
    # train_all_models_thread.start()
    
    load_thread.join()
    consumers_thread.join()
    # train_all_models_thread.join()