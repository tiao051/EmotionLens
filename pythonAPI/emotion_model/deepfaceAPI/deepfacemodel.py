from deepface import DeepFace 
import numpy as np

def load_deepface_model():
    try:
        # Tạo một ảnh dummy để khởi động mô hình
        # Ảnh dummy có thể là bất kỳ ảnh nào, ví dụ ảnh đen (hoặc ảnh từ một file thực tế)
        dummy_image = np.zeros((48, 48, 3), dtype=np.uint8)  # Ảnh đen có kích thước 48x48

        # Phân tích ảnh dummy để tải mô hình
        DeepFace.analyze(img_path=dummy_image, actions=['emotion'], enforce_detection=False)
        print("DeepFace models loaded successfully.")

    except Exception as e:
        print(f"❌ Error loading DeepFace models: {e}")
        
# Hàm phân tích cảm xúc từ ảnh
def analyze_image_emotion(image_path):
    try:
        # Phân tích cảm xúc
        result = DeepFace.analyze(
            img_path=image_path,
            actions=['emotion'],
            enforce_detection=True,
            detector_backend='retinaface'
        )

        if result and isinstance(result, list) and len(result) > 0:
            first_face_result = result[0]
            dominant_emotion = first_face_result.get('dominant_emotion')
            emotion_scores = first_face_result.get('emotion')

            print(f"\n📷 Emotion Analysis for the image: {image_path}")
            print(f"🎯 Dominant Emotion: {dominant_emotion}")
            print(f"📊 Emotion Scores: {emotion_scores}")

            return dominant_emotion
        else:
            print(f"⚠️ No face detected in the image: {image_path}")
            return None

    except Exception as e:
        print(f"❌ Error analyzing the image: {e}")
        return None
