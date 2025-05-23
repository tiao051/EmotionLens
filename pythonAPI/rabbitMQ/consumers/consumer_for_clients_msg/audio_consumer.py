import json
from rabbitMQ.services.api_client import send_to_api_async
from config import API_ENDPOINTS

def create_audio_callback(model, label_encoder):
    from emotion_model.audio_model.audio_emotion import AudioFeatureExtractor
    import numpy as np
    feature_extractor = AudioFeatureExtractor()

    async def callback_audio(ch, method, properties, body):
        message = json.loads(body)
        file_id = message.get("Id")
        file_path = message.get("FilePath")
        section_index = message.get("section_index", None)

        if section_index is not None:
            print(f"Received section_index: {section_index}")
        else:
            print("No section_index found in message")

        print(f"Received ID: {file_id}")
        print(f"Received audio content: {file_path}")

        try:
            # Trích xuất đặc trưng MFCC
            features = feature_extractor.extract_mfcc_from_file(file_path)

            # Dự đoán xác suất các lớp
            probs = model.predict(features)[0]
            pred_idx = np.argmax(probs)
            emotion_result = label_encoder.inverse_transform([pred_idx])[0]

            print(f"Emotion analysis result for ID {file_id}: {emotion_result}")

            if section_index is not None:
                result_message = {
                    "VideoId": file_id,
                    "Section": section_index,
                    "Emotion": emotion_result,
                    "Probs": {label: float(prob) for label, prob in zip(label_encoder.classes_, probs)}
                }
                print(f"Send multi audio to C#: Section {section_index}")
                await send_to_api_async(result_message, API_ENDPOINTS["multi_audio"])
            else:
                result_message = {
                    "Id": file_id,
                    "Emotion": emotion_result,
                    "Probs": {label: float(prob) for label, prob in zip(label_encoder.classes_, probs)}
                }
                print("Send single audio to C#")
                await send_to_api_async(result_message, API_ENDPOINTS["audio"])

            print(f"Data sent to C#: {result_message}")

        except Exception as e:
            print(f"Error processing audio with ID {file_id}: {e}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        print(f"Audio with ID: {file_id} processed and acknowledged.")

    return callback_audio

