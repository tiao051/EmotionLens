import threading
import asyncio
import warnings
warnings.filterwarnings("ignore")
# from tensorflow.keras.models import load_model as keras_load_model  # type: ignore
# from tensorflow.keras.models import load_model  # type: ignore
from rabbitMQ.connection.connection import get_rabbitmq_connection
from emotion_model.efficientNet_model.build import build_finetune_efficientnet

from rabbitMQ.consumers.consumer_for_clients_msg import (
    audio_consumer,
    image_consumer,
    tiktok_consumer,
    text_consumer,
    url_consumer,
)
from rabbitMQ.consumers.consumer_for_python_services import (
    frame_consumer,
    comments_consumer
)
# ✅ Wrapper xử lý chạy async task an toàn
def run_async_task(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(coro)
    loop.close()
    return result

def load_audio_model():
    from emotion_model.audio_model.audio_emotion import EmotionRecognitionModel
    import numpy as np
    import os
    from sklearn.preprocessing import LabelEncoder

    audio_model_path = os.path.join(os.path.dirname(__file__), 'emotion_model', 'audio_model', 'crema_d_audio_emotion_bilstm.keras')
    audio_labels_path = os.path.join(os.path.dirname(__file__), 'emotion_model', 'audio_model', 'crema_d_labels_seq.npy')
    audio_model = EmotionRecognitionModel()
    audio_model.load_model(audio_model_path)
    audio_labels = np.load(audio_labels_path)
    audio_label_encoder = LabelEncoder()
    audio_label_encoder.fit(audio_labels)
    audio_callback = audio_consumer.create_audio_callback(audio_model, audio_label_encoder)
    return audio_callback

def train_all_models():
    from emotion_model.efficientNet_model.train import train_efficientnet_emotion_model
    train_efficientnet_emotion_model()

def load_all_models():
    text_consumer.load_text_model()
    comments_consumer.load_text_model()
    # load_audio_model()
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
        try:
            connection.close()
            print(f"✅ Closed connection to RabbitMQ {queue_name}.")
        except Exception as e:
            print(f"⚠️ Connection already closed or error on close: {e}")

def start_all_consumers():
    # Load models
    efficientnet_model = build_finetune_efficientnet(input_shape=(48, 48, 3), num_classes=7)
    img_callback = image_consumer.create_img_callback(efficientnet_model)
    audio_callback = load_audio_model()
    
    consumers = [
        {"queue": "txt_queue", "callback": lambda ch, m, p, b: run_async_task(text_consumer.callback_txt(ch, m, p, b))},
        {"queue": "audio_queue", "callback": lambda ch, m, p, b: run_async_task(audio_callback(ch, m, p, b))},
        {"queue": "img_queue", "callback": lambda ch, m, p, b: run_async_task(img_callback(ch, m, p, b))},
        {"queue": "tiktok_queue", "callback": lambda ch, m, p, b: run_async_task(tiktok_consumer.process_tiktok_callbacks(ch, m, p, b))},
        {"queue": "csv_queue", "callback": url_consumer.callback_url}, 
        {"queue": "fps_queue", "callback": lambda ch, m , p, b: run_async_task(frame_consumer.callback_frame(ch, m, p, b))},
        {"queue": "comment_queue", "callback": lambda ch, m , p, b: run_async_task(comments_consumer.callback_comment(ch, m, p, b))},
        {"queue": "audio_sections_queue", "callback": lambda ch, m, p, b: run_async_task(audio_callback(ch, m, p, b))}

    ]

    threads = []
    for c in consumers:
        thread = threading.Thread(target=start_consumer, args=(c["queue"], c["callback"]))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

if __name__ == "__main__":
    print("🎯 Starting all RabbitMQ consumers and model loading...")

    # Chạy load_all_models song song với consumers
    load_thread = threading.Thread(target=load_all_models)
    consumers_thread = threading.Thread(target=start_all_consumers)

    load_thread.start()
    consumers_thread.start()
    
    load_thread.join()
    consumers_thread.join()
