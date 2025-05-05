import threading
import asyncio
from tiktokAPI.tiktokcrawldata import get_comments
from emotion_model.deepfaceAPI.deepfacemodel import load_or_download_model, analyze_image_emotion
from rabbitMQ.consumer import start_rabbitmq_consumer
from emotion_model.img_model.train import train_model
from emotion_model.img_model.train import create_data_generators
from emotion_model.img_model.predict import predict_emotion
from emotion_model.img_model.build import build_emotion_model
from utils.image_utils import choose_image_file
from tensorflow.keras.models import load_model
# from model.audio_model.data_preparation import prepare_audio_data
# from model.audio_model.predict import evaluate_audio_model


# Hàm chạy consumer trong một thread riêng
def run_rabbitmq_consumer():
    start_rabbitmq_consumer()

# Hàm huấn luyện mô hình
def train_img_emotion_model():
    train_dir = 'D:/Deep_Learning/dataSet/fer2013/train'
    test_dir = 'D:/Deep_Learning/dataSet/fer2013/test'

    train_gen, test_gen = create_data_generators(train_dir, test_dir)
    emotion_model = build_emotion_model()
    train_model(emotion_model, train_gen, test_gen, epochs=10)

    img_path = choose_image_file()
    loaded_model = load_model('emotion_model.h5')
    predict_emotion(loaded_model, img_path)

# Phân tích cảm xúc từ hình ảnh với DeepFace
def analyze_emotion_from_image(image_path): 
    model_name = "VGG-Face"
    model = load_or_download_model(model_name)
    
    if model:
        analyze_image_emotion(image_path, model)
    else:
        print("Model loading failed. Cannot proceed.")

# def analyze_emotion_from_audio(features_path, labels_path, model_path):
#     audio_model = load_model(model_path)

#     _, X_test, _, y_test, _, label_encoder = prepare_audio_data(features_path, labels_path)

#     y_pred, y_true = evaluate_audio_model(audio_model, X_test, y_test, label_encoder)
#     return y_pred, y_true
    

if __name__ == "__main__":
    consumer_thread = threading.Thread(target=run_rabbitmq_consumer)
    consumer_thread.start()
    
    # asyncio.run(get_comments())  # Nếu cần crawling comment

    image_path = "D:/Deep_Learning/dataSet/imgTest/img.jpg"
    # model_path = "D:/Deep_Learning/main/pythonAPI/model/crema_d_audio_emotion_bilstm_attention.h5"
    analyze_emotion_from_image(image_path)
    # train_img_emotion_model()

