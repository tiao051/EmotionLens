# import numpy as np
# from tensorflow.keras.preprocessing import image
# from tensorflow.keras.models import load_model
# import matplotlib.pyplot as plt

# emotion_labels = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

# def predict_emotion(model, img_path):
#     if not img_path:
#         print("No image selected. Exiting.")
#         return

#     img = image.load_img(img_path, target_size=(48, 48), color_mode='grayscale')
#     img_array = image.img_to_array(img) / 255.0
#     img_array = np.expand_dims(img_array, axis=0)

#     prediction = model.predict(img_array)
#     predicted_class = np.argmax(prediction)

#     print(f'Predicted Emotion: {emotion_labels[predicted_class]}')
#     print("Probability distribution:")
#     for i, prob in enumerate(prediction[0]):
#         print(f"{emotion_labels[i]}: {prob:.2%}")

#     # Show image with prediction
#     plt.imshow(img, cmap='gray')
#     plt.title(f'Predicted: {emotion_labels[predicted_class]}')
#     plt.axis('off')
#     plt.show()
