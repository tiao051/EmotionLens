import os
from deepface import DeepFace
from tensorflow.keras.models import load_model

# Hàm tải hoặc tải lại mô hình từ file (có cache)
def load_or_download_model(model_name="VGG-Face"):
    try:
        model = DeepFace.build_model(model_name)
        print(f"{model_name} model loaded successfully.")
        return model
    except Exception as e:
        print(f"Error downloading/loading model: {e}")
        return None

# Hàm phân tích cảm xúc từ ảnh
def analyze_image_emotion(image_path, model):
    try:
        result = DeepFace.analyze(
            img_path=image_path,
            actions=['emotion'],
            enforce_detection=False
        )

        if result and isinstance(result, list) and len(result) > 0:
            first_face_result = result[0]
            dominant_emotion = first_face_result['dominant_emotion']
            emotion_scores = first_face_result['emotion']

            print(f"\n📷 Emotion Analysis for the image: {image_path}")
            print(f"🎯 Dominant Emotion: {dominant_emotion}")
            print(f"📊 Emotion Scores: {emotion_scores}")

            return dominant_emotion
        else:
            print(f"No face detected in the image: {image_path}")
            return None, None

    except Exception as e:
        print(f"Error analyzing the image: {e}")
        return None, None
