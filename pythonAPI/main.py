import threading
from rabbitMQ.consumer import start_consumer
from rabbitMQ.consumer import callback_txt, callback_audio, callback_img, callback_url

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
        {"queue": "txt_queue", "callback": callback_txt},
        {"queue": "audio_queue", "callback": callback_audio},
        {"queue": "img_queue", "callback": callback_img},
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
    print("🎯 Starting all RabbitMQ consumers...")
    start_all_consumers()
