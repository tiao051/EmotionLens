import json
import numpy as np
from rabbitMQ.services.emotion_service import analyze_with_deepface
from rabbitMQ.services.api_client import send_to_api_async
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from config import API_ENDPOINTS

async def callback_img(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    file_path = message.get("FilePath")

    print(f"[Image] Received ID: {file_id}, Path: {file_path}")
    try:
        emotion = analyze_with_deepface(file_path)
        result = { "Id": file_id, "Emotion": emotion }
        await send_to_api_async(result, API_ENDPOINTS["image"])
    except Exception as e:
        print(f"❌ Error: {e}")
    ch.basic_ack(delivery_tag=method.delivery_tag)
    
def create_img_callback(model):
    async def callback_img_realmodel(ch, method, properties, body):
        message = json.loads(body)
        file_id = message.get("Id")
        file_path = message.get("FilePath")

        print(f"Received ID: {file_id}")
        print(f"Received image path: {file_path}")

        try:
            # Load và tiền xử lý ảnh
            img = load_img(file_path, target_size=(48, 48), color_mode='grayscale')
            img_array = img_to_array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)

            # Dự đoán cảm xúc bằng model đã truyền từ main.py
            prediction = model.predict(img_array)
            predicted_class = np.argmax(prediction)
            emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
            emotion_result = emotion_labels[predicted_class]

            print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

            # Chuẩn bị kết quả gửi đi
            result_message = {
                "Id": file_id,
                "Emotion": emotion_result
            }
            print(f"Data sent to C#: {result_message}")

            # Gửi kết quả đến API
            await send_to_api_async(result_message, API_ENDPOINTS["image"])

        except Exception as e:
            print(f"Error processing image with ID {file_id}: {e}")

        # Xác nhận đã xử lý xong message
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Image with ID: {file_id} processed and acknowledged.")

    return callback_img_realmodel
