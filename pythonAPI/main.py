import threading
import asyncio
# from tensorflow.keras.models import load_model as keras_load_model
from emotion_model.deepfaceAPI.deepfacemodel import load_deepface_model
from tensorflow.keras.models import load_model
from rabbitMQ.connection.connection import get_rabbitmq_connection
from rabbitMQ.consumers import (
    audio_consumer,
    image_consumer,
    tiktok_consumer,
    text_consumer,
    url_consumer,
)

# AUDIO_MODEL_PATH = r"D:\Deep_Learning\main\pythonAPI\emotion_model\audio_model\audio_model.h5"
# IMG_MODEL_PATH = r"D:\Deep_Learning\main\pythonAPI\emotion_model\img_model\img_model.h5"

# audio_model = keras_load_model(AUDIO_MODEL_PATH)
# img_model = load_model(IMG_MODEL_PATH)
# img_callback = image_consumer.create_img_callback(img_model)

# Optional: mô hình huấn luyện hình ảnh
def train_img_emotion_model():
    from emotion_model.img_model.build import build_improved_emotion_model
    from emotion_model.img_model.train import create_data_generators, train_model

    train_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/train'
    test_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/test'

    # Tạo data generators
    print("🔄 Creating data generators...")
    train_gen, test_gen = create_data_generators(train_dir, test_dir)

    # Xây dựng model
    print("🔨 Building the emotion model...")
    model = build_improved_emotion_model(input_shape=(48, 48, 1), num_classes=7)
    model.summary()

    # Train model
    print("🚀 Training the model...")
    train_model(model, train_gen, test_gen, epochs=50, model_dir='D:/Deep_Learning/main/pythonAPI/emotion_model/img_model/models')
    print("✅ Training completed. Model saved in 'models' directory.")

def start_consumer(queue_name, callback):
    print(f"🚀 Starting RabbitMQ consumer for {queue_name}...")
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
    load_deepface_model()
    consumers = [
        {"queue": "txt_queue", "callback": lambda ch, m, p, b: asyncio.run(text_consumer.callback_txt(ch, m, p, b))},
        # {"queue": "audio_queue", "callback": lambda ch, m, p, b: asyncio.run(audio_consumer.create_audio_callback(audio_model)(ch, m, p, b))},
        {"queue": "img_queue", "callback": lambda ch, m, p, b: asyncio.run(image_consumer.callback_img(ch, m, p, b))},
        # {"queue": "img_queue", "callback": lambda ch, m, p, b: asyncio.run(img_callback()(ch, m, p, b))},
        {"queue": "tiktok_queue", "callback": lambda ch, m, p, b: asyncio.run(tiktok_consumer.callback_tiktok(ch, m, p, b))},
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
    print("🎯 Starting all RabbitMQ consumers...")
    start_all_consumers()
    # train_img_emotion_model()