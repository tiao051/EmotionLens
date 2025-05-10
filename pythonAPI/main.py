import threading
import asyncio
# from tensorflow.keras.models import load_model as keras_load_model
from emotion_model.deepfaceAPI.deepfacemodel import load_deepface_model
from rabbitMQ.consumer import (
    start_consumer,
    callback_txt,
    callback_url,
    create_img_callback,
    callback_img,
    callback_tiktok,
    create_audio_callback
)

# AUDIO_MODEL_PATH = r"D:\Deep_Learning\main\pythonAPI\emotion_model\audio_model\audio_model.h5"
IMG_MODEL_PATH = r"D:\Deep_Learning\main\pythonAPI\emotion_model\img_model\img_model.h5"

# audio_model = keras_load_model(AUDIO_MODEL_PATH)
# img_model = load_model(IMG_MODEL_PATH)
# img_callback = create_img_callback(img_model)
    
# def test_predict_text(text="happy", model_directory="./sentiment_distilbert_full_data"):
#     model, tokenizer = text_load_model(model_directory)
#     label, idx = predict_sentiment(text, model, tokenizer)
#     print(f"Input: {text}\nPredicted: {label} (Index: {idx})")
#     return label, idx

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

def start_all_consumers():
    load_deepface_model()
    consumers = [
        {"queue": "txt_queue", "callback": lambda ch, m, p, b: asyncio.run(callback_txt(ch, m, p, b))},
        # {"queue": "audio_queue", "callback": lambda ch, m, p, b: asyncio.run(create_audio_callback(audio_model)(ch, m, p, b))},
        {"queue": "img_queue", "callback": lambda ch, m, p, b: asyncio.run(callback_img(ch, m, p, b))},
        # {"queue": "img_queue", "callback": lambda ch, m, p, b: asyncio.run(img_callback()(ch, m, p, b))},
        {"queue": "tiktok_queue", "callback": lambda ch, m, p, b: asyncio.run(callback_tiktok(ch, m, p, b))},
        {"queue": "csv_queue", "callback": callback_url} 
    ]

    threads = []
    for c in consumers:
        thread = threading.Thread(target=start_consumer, args=(c["queue"], c["callback"]))
        thread.start()
        threads.append(thread)

    for t in threads:
        t.join()

if __name__ == "__main__":
    # test_predict_text("happy")
    print("🎯 Starting all RabbitMQ consumers...")
    start_all_consumers()
    train_img_emotion_model()