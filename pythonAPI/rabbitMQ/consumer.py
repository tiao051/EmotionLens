# import json
# import pika
# import threading
# import aiohttp
# import time
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'emotion_model')))
# import urllib3
# from tensorflow.keras.preprocessing.image import load_img, img_to_array
# import numpy as np
# urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# from emotion_model.deepfaceAPI.deepfacemodel import analyze_image_emotion
# from config import RABBITMQ_CONFIG, API_ENDPOINTS, TIKTOK_API_CONFIG
# from tiktokAPI.tiktokcrawldata import extract_video_id, get_comments 

# def get_rabbitmq_connection():
#     connection_event = threading.Event()
#     connection = None

#     def connect():
#         nonlocal connection
#         while True:
#             try:
#                 connection = pika.BlockingConnection(pika.ConnectionParameters(
#                     host=RABBITMQ_CONFIG["host"],
#                     port=RABBITMQ_CONFIG["port"],
#                     credentials=pika.PlainCredentials(
#                         RABBITMQ_CONFIG["username"],
#                         RABBITMQ_CONFIG["password"]
#                     )
#                 ))
#                 print("✅ Connected to RabbitMQ (consumer)")
#                 connection_event.set()
#                 break
#             except pika.exceptions.AMQPConnectionError as e:
#                 print(f"❌ Failed to connect to RabbitMQ: {e}. Retrying in 5 seconds...")
#                 time.sleep(5)
#     connection_thread = threading.Thread(target=connect)
#     connection_thread.start()
#     connection_event.wait()
#     return connection

# def callback_url(ch, method, properties, body):
#     message = json.loads(body)
#     file_id = message.get("Id")
#     file_path = message.get("FilePath")
    
#     print(f"Received ID: {file_id}")
#     print(f"Received file path: {file_path}")
#     # xử lý file tại đây...
#     ch.basic_ack(delivery_tag=method.delivery_tag)
#     print(f"File with ID: {file_id} processed and acknowledged.")

# async def callback_img(ch, method, properties, body):
#     message = json.loads(body)
#     file_id = message.get("Id")
#     file_path = message.get("FilePath")

#     print(f"Received ID: {file_id}")
#     print(f"Received image path: {file_path}")

#     try:
#         # Gọi DeepFace phân tích
#         emotion_result = analyze_image_emotion(file_path)

#         # Trường hợp không phát hiện mặt hoặc lỗi
#         if not emotion_result:
#             emotion_result = "Unknown"

#         print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

#         result_message = {
#             "Id": file_id,
#             "Emotion": emotion_result
#         }
#         print(f"Data sent to C#: {result_message}")

#         await send_to_api_async(result_message, API_ENDPOINTS["image"])

#     except Exception as e:
#         print(f"Error processing image with ID {file_id}: {e}")

#     ch.basic_ack(delivery_tag=method.delivery_tag)
#     print(f"Image with ID: {file_id} processed and acknowledged.")
    
# def create_img_callback(model):
#     async def callback_img_realmodel(ch, method, properties, body):
#         message = json.loads(body)
#         file_id = message.get("Id")
#         file_path = message.get("FilePath")

#         print(f"Received ID: {file_id}")
#         print(f"Received image path: {file_path}")

#         try:
#             # Load và tiền xử lý ảnh
#             img = load_img(file_path, target_size=(48, 48), color_mode='grayscale')
#             img_array = img_to_array(img) / 255.0
#             img_array = np.expand_dims(img_array, axis=0)

#             # Dự đoán cảm xúc bằng model đã truyền từ main.py
#             prediction = model.predict(img_array)
#             predicted_class = np.argmax(prediction)
#             emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
#             emotion_result = emotion_labels[predicted_class]

#             print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

#             # Chuẩn bị kết quả gửi đi
#             result_message = {
#                 "Id": file_id,
#                 "Emotion": emotion_result
#             }
#             print(f"Data sent to C#: {result_message}")

#             # Gửi kết quả đến API
#             await send_to_api_async(result_message, API_ENDPOINTS["image"])

#         except Exception as e:
#             print(f"Error processing image with ID {file_id}: {e}")

#         # Xác nhận đã xử lý xong message
#         ch.basic_ack(delivery_tag=method.delivery_tag)
#         print(f"Image with ID: {file_id} processed and acknowledged.")

#     return callback_img_realmodel
    
# async def callback_txt(ch, method, properties, body):
#     message = json.loads(body)
#     file_id = message.get("Id")
#     text_content = message.get("Text")

#     print(f"Received ID: {file_id}")
#     print(f"Received text content: {text_content}")

#     try:
#         emotion_result = "Happy" 

#         print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

#         result_message = {
#             "Id": file_id,
#             "Emotion": emotion_result
#         }
#         print(f"Data sent to C#: {result_message}")

#         await send_to_api_async(result_message, API_ENDPOINTS["text"])

#     except Exception as e:
#         print(f"Error processing text with ID {file_id}: {e}")


#     ch.basic_ack(delivery_tag=method.delivery_tag)
#     print(f"Text with ID: {file_id} processed and acknowledged.")

# def create_audio_callback(model):
#     async def callback_audio(ch, method, properties, body):
#         message = json.loads(body)
#         file_id = message.get("Id")
#         file_path = message.get("FilePath")

#         print(f"Received ID: {file_id}")
#         print(f"Received audio content: {file_path}")

#         try:
#             emotion_result = "Happy"  

#             print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

#             result_message = {
#                 "Id": file_id,
#                 "Emotion": emotion_result
#             }
#             print(f"Data sent to C#: {result_message}")

#             await send_to_api_async(result_message, API_ENDPOINTS["audio"])

#         except Exception as e:
#             print(f"Error processing text with ID {file_id}: {e}")

#         ch.basic_ack(delivery_tag=method.delivery_tag)
#         print(f"Audio with ID: {file_id} processed and acknowledged.")
#     return callback_audio

# async def callback_tiktok(ch, method, properties, body):
#     message = json.loads(body)
#     file_id = message.get("Id")
#     url_content = message.get("Url")
    
#     if url_content:
#         print(f"Received ID: {file_id}")
#         print(f"Received URL: {url_content}")
        
#         video_id = extract_video_id(url_content)
#         if not video_id:
#             print("❌ Không thể lấy video_id từ URL.")
#             ch.basic_ack(delivery_tag=method.delivery_tag)
#             return

#         print(f"Extracted video ID: {video_id}")
        
#         ms_token = TIKTOK_API_CONFIG["ms_token"]
#         output_path = os.path.join(TIKTOK_API_CONFIG["save_csv_path"], f"comments_{video_id}.csv")
        
#         try:
#             await get_comments(video_id, ms_token, output_path)
#             print(f"Successfully crawled comments for video ID {video_id}")
#         except Exception as e:
#             print(f"Error crawling TikTok data for video ID {video_id}: {e}")

#     ch.basic_ack(delivery_tag=method.delivery_tag)
#     print(f"Tiktok URL with ID: {file_id} processed and acknowledged.")
    
# def start_consumer(queue_name, callback):
#     print(f"🚀 Starting RabbitMQ consumer for {queue_name}...")
#     connection = get_rabbitmq_connection()
#     if connection is None:
#         print(f"❌ Failed to connect to RabbitMQ {queue_name}.")
#         return

#     channel = connection.channel()
#     channel.queue_declare(queue=queue_name, durable=True)
#     channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=False)

#     print(f"⏳ Waiting for messages in {queue_name}.")
#     try:
#         channel.start_consuming()
#     except KeyboardInterrupt:
#         print(f"🛑 Stopping {queue_name} consumer...")
#         channel.stop_consuming()
#     finally:
#         connection.close()
#         print(f"✅ Closed connection to RabbitMQ {queue_name}.")
        
# async def send_to_api_async(data, api_url):
#     headers = {"Content-Type": "application/json"}
#     async with aiohttp.ClientSession() as session:
#         try:
#             async with session.post(api_url, json=data, headers=headers, ssl=False) as response:
#                 if response.status == 200:
#                     print(f"Successfully sent data to C#: {response.status}, {await response.text()}")
#                 else:
#                     print(f"Failed to send data to C#: {response.status}, {await response.text()}")
#         except Exception as e:
#             print(f"Error sending data to C#: {e}")
        