import threading
import asyncio
from tiktokAPI.tiktokcrawldata import get_comments
from emotion_model.deepfaceAPI.deepfacemodel import load_or_download_model, analyze_image_emotion
from rabbitMQ.consumer import start_url_rabbitmq_consumer
from rabbitMQ.consumer import start_img_queue_consumer
from rabbitMQ.consumer import start_txt_rabbitmq_consumer
from rabbitMQ.consumer import start_audio_rabbitmq_consumer
from emotion_model.img_model.train import train_model
from emotion_model.img_model.train import create_data_generators
from emotion_model.img_model.predict import predict_emotion
from emotion_model.img_model.build import build_emotion_model
from utils.image_utils import choose_image_file
from tensorflow.keras.models import load_model # type: ignore
# from model.audio_model.data_preparation import prepare_audio_data
# from model.audio_model.predict import evaluate_audio_model

# Hàm chạy consumer trong một thread riêng
def run_url_rabbitmq_consumer():
    start_url_rabbitmq_consumer()

def run_rabbitmq_img_consumer():
    start_img_queue_consumer()
    
def run_txt_rabbitmq_consumer():
    start_txt_rabbitmq_consumer()
    
def run_audio_rabbitmq_consumer():
    start_audio_rabbitmq_consumer()
# Hàm huấn luyện mô hình
def train_img_emotion_model():
    train_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/train'
    test_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/test'

    train_gen, test_gen = create_data_generators(train_dir, test_dir)
    emotion_model = build_emotion_model()
    train_model(emotion_model, train_gen, test_gen, epochs=10)

    img_path = choose_image_file()
    loaded_model = load_model('emotion_model.h5')
    predict_emotion(loaded_model, img_path)

if __name__ == "__main__":
    consumer_thread = threading.Thread(target=run_url_rabbitmq_consumer)
    consumer_thread.start()

    img_consumer_thread = threading.Thread(target=run_rabbitmq_img_consumer)
    img_consumer_thread.start()
    
    txt_consumer_thread = threading.Thread(target=run_txt_rabbitmq_consumer)
    txt_consumer_thread.start()
    
    audio_consumer_thread = threading.Thread(target=run_audio_rabbitmq_consumer)
    audio_consumer_thread.start()

    # asyncio.run(get_comments())  # Nếu cần crawling comment

    # image_path = "D:/Deep_Learning/dataSet/testData/imgTest/img.jpg"
    # model_path = "D:/Deep_Learning/main/pythonAPI/model/crema_d_audio_emotion_bilstm_attention.h5"
    # analyze_emotion_from_image(image_path)
    # train_img_emotion_model()

