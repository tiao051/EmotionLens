import threading
import asyncio
from keras.models import load_model # type: ignore
from emotion_model.text_model.predict import load_model, predict_sentiment
from rabbitMQ.consumer import (
    start_consumer,
    callback_txt,
    callback_img,
    callback_url,
    callback_tiktok,
    create_audio_callback
)

AUDIO_MODEL_PATH = r"D:\Deep_Learning\main\pythonAPI\emotion_model\audio_model\audio_model.h5"
audio_model = load_model(AUDIO_MODEL_PATH)

def test_predict_text(text="happy", model_directory="./sentiment_distilbert_full_data"):
    model, tokenizer = load_model(model_directory)
    label, idx = predict_sentiment(text, model, tokenizer)
    print(f"Input: {text}\nPredicted: {label} (Index: {idx})")
    return label, idx

# Optional: mô hình huấn luyện hình ảnh
def train_img_emotion_model():
    from emotion_model.model_training import create_data_generators, build_emotion_model, train_model # type: ignore
    from keras.models import load_model # type: ignore
    from emotion_model.inference import predict_emotion # type: ignore

    train_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/train'
    test_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/test'

    train_gen, test_gen = create_data_generators(train_dir, test_dir)
    emotion_model = build_emotion_model()
    train_model(emotion_model, train_gen, test_gen, epochs=10)
    loaded_model = load_model('emotion_model.h5')
    predict_emotion(loaded_model)

def start_all_consumers():
    consumers = [
        {"queue": "txt_queue", "callback": lambda ch, m, p, b: asyncio.run(callback_txt(ch, m, p, b))},
        {"queue": "audio_queue", "callback": lambda ch, m, p, b: asyncio.run(create_audio_callback(audio_model)(ch, m, p, b))},
        {"queue": "img_queue", "callback": lambda ch, m, p, b: asyncio.run(callback_img(ch, m, p, b))},
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
    test_predict_text("happy")
    print("🎯 Starting all RabbitMQ consumers...")
    start_all_consumers()
