import os
import warnings
import logging
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore") 
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

logging.basicConfig(
    level=logging.WARNING,  
    format='%(asctime)s | %(levelname)s | %(message)s',
)

logging.getLogger("transformers").setLevel(logging.ERROR)
logging.getLogger("torch").setLevel(logging.ERROR)
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

from tensorflow.keras.models import load_model
from rabbitMQ.connection.connection import get_rabbitmq_connection

from rabbitMQ.consumers.consumer_for_clients_msg import (
    audio_consumer,
    image_consumer,
    tiktok_consumer,
    text_consumer,
    url_consumer,
)
from rabbitMQ.consumers.consumer_for_python_services import (
    frame_consumer,
    comments_consumer,
)

def train_text_model():
    from emotion_model.text_model.text_train import train_text_model
    train_text_model()
def train_img_model():
    from emotion_model.efficientNet_model.train import train_efficientnet_emotion_model
    train_efficientnet_emotion_model()
def run_async_task(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        return asyncio.create_task(coro)
    else:
        return loop.run_until_complete(coro)

def load_audio_model():    
    from emotion_model.audio_model.audio_emotion import EmotionRecognitionModel
    import numpy as np
    from sklearn.preprocessing import LabelEncoder

    base_dir = Path(__file__).parent / 'emotion_model' / 'audio_model'
    model_path = base_dir / 'crema_d_audio_emotion_bilstm.keras'
    labels_path = base_dir / 'crema_d_labels_seq.npy'

    audio_model = EmotionRecognitionModel()
    audio_model.load_model(str(model_path))

    audio_labels = np.load(labels_path)
    audio_label_encoder = LabelEncoder()
    audio_label_encoder.fit(audio_labels)

    logging.warning(f"Audio model loaded successfully from {model_path}")
    return audio_consumer.create_audio_callback(audio_model, audio_label_encoder)

def load_text_model():
    model_path = Path("D:/Deep_Learning/main/pythonAPI/emotion_model/text_model/text_model.keras")

    model = load_model(model_path)
    logging.warning(f"Text model loaded successfully from {model_path}")
    return model

def load_image_model():
    model_path = Path("D:/Deep_Learning/main/pythonAPI/emotion_model/efficientNet_model/efficientnet_emotion_model/efficientnet_emotion_model.keras")
    
    model = load_model(model_path)
    logging.warning(f"Image EfficientNet model loaded successfully from {model_path}")
    return model

def load_restNet_model():
    model_path = Path("D:/Deep_Learning/main/pythonAPI/emotion_model/restNet_model/fer2013_resnet50_best.keras")
    
    model = load_model(model_path, compile=False)
    logging.warning(f"Image RestNet model loaded successfully from {model_path}")
    return model

def start_consumer(queue_name, callback):
    connection = get_rabbitmq_connection()
    if connection is None:
        logging.error(f"Failed to connect to RabbitMQ {queue_name}")
        return
    channel = connection.channel()
    channel.queue_declare(queue=queue_name, durable=True)
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)
    logging.warning(f"Waiting for messages in queue: {queue_name}")
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        logging.warning(f"Stopping consumer for queue: {queue_name}")
        channel.stop_consuming()
    finally:
        try:
            connection.close()
            logging.warning(f"Connection to RabbitMQ closed for queue: {queue_name}")
        except Exception as e:
            logging.warning(f"Error closing RabbitMQ connection for {queue_name}: {e}")

def start_all_consumers():
    image_model = load_restNet_model()
    img_callback = image_consumer.create_img_callback(image_model)
    
    text_model, tokenizer, id2label = load_text_model()
    text_callback = text_consumer.create_text_callback(text_model, tokenizer, id2label)
    comment_callback = comments_consumer.create_comment_callback(text_model, tokenizer, id2label)

    audio_callback = load_audio_model()

    consumers = [
        {"queue": "txt_queue", "callback": lambda ch, m, p, b: run_async_task(text_callback(ch, m, p, b))},
        {"queue": "audio_queue", "callback": lambda ch, m, p, b: run_async_task(audio_callback(ch, m, p, b))},
        {"queue": "img_queue", "callback": lambda ch, m, p, b: run_async_task(img_callback(ch, m, p, b))},
        {"queue": "tiktok_queue", "callback": lambda ch, m, p, b: run_async_task(tiktok_consumer.process_tiktok_callbacks(ch, m, p, b))},
        {"queue": "csv_queue", "callback": url_consumer.callback_url},
        {"queue": "fps_queue", "callback": lambda ch, m, p, b: run_async_task(frame_consumer.callback_frame(ch, m, p, b))},
        {"queue": "comment_queue", "callback": lambda ch, m, p, b: run_async_task(comment_callback(ch, m, p, b))},
        {"queue": "audio_sections_queue", "callback": lambda ch, m, p, b: run_async_task(audio_callback(ch, m, p, b))},
    ]

    with ThreadPoolExecutor(max_workers=len(consumers)) as executor:
        futures = [executor.submit(start_consumer, c["queue"], c["callback"]) for c in consumers]
        for f in futures:
            f.result()

if __name__ == "__main__":
    # logging.warning("Starting train models..")
    # train_img_model()
    logging.warning("Starting all RabbitMQ consumers and loading models...")
    start_all_consumers()
    logging.warning("All consumers started successfully.")