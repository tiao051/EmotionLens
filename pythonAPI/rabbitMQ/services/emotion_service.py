from emotion_model.deepfaceAPI.deepfacemodel import analyze_image_emotion
from tensorflow.keras.preprocessing.image  import load_img, img_to_array #type: ignore
import numpy as np

def analyze_with_deepface(file_path):
    return analyze_image_emotion(file_path) or "Unknown"

def analyze_with_model(file_path, model):
    
    img = load_img(file_path, target_size=(48, 48), color_mode='grayscale')
    img_array = img_to_array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    prediction = model.predict(img_array)
    predicted_class = np.argmax(prediction)
    emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
    return emotion_labels[predicted_class]

