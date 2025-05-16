# from tensorflow.keras.preprocessing.image import ImageDataGenerator # type: ignore
# from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint # type: ignore
# from emotion_model.img_model.build import build_improved_emotion_model
# import matplotlib.pyplot as plt
# import os

# def create_data_generators(train_dir, test_dir, batch_size=128):
#     # Augmentation for the training data
#     train_datagen = ImageDataGenerator(
#         rescale=1./255,
#         rotation_range=25,
#         width_shift_range=0.25,
#         height_shift_range=0.25,
#         shear_range=0.18,
#         zoom_range=0.18,
#         brightness_range=(0.8, 1.2),
#         horizontal_flip=True,
#         fill_mode='nearest'
#     )
#     # Only rescaling for the test data (no augmentation)
#     test_datagen = ImageDataGenerator(rescale=1./255)

#     train_generator = train_datagen.flow_from_directory(
#         train_dir,
#         target_size=(48, 48),
#         color_mode='grayscale',
#         batch_size=batch_size,
#         class_mode='categorical',
#         shuffle=True  # Shuffling the training data
#     )

#     test_generator = test_datagen.flow_from_directory(
#         test_dir,
#         target_size=(48, 48),
#         color_mode='grayscale',
#         batch_size=batch_size,
#         class_mode='categorical',
#         shuffle=False  # No shuffling on test data
#     )

#     return train_generator, test_generator

# def train_model(model, train_generator, test_generator, epochs=80, model_dir='models'):
#     os.makedirs(model_dir, exist_ok=True)  # Ensure the directory exists

#     # ModelCheckpoint lưu model ra file .keras (chuẩn Keras 3.x+)
#     checkpoint_path = os.path.join(model_dir, "best_model.keras")
#     callbacks = [
#         EarlyStopping(monitor='val_accuracy', patience=12, restore_best_weights=True),
#         ReduceLROnPlateau(monitor='val_accuracy', factor=0.2, patience=6, min_lr=1e-6),
#         ModelCheckpoint(checkpoint_path, monitor='val_accuracy', save_best_only=True, save_weights_only=False)
#     ]

#     history = model.fit(
#         train_generator,
#         epochs=epochs,
#         validation_data=test_generator,
#         callbacks=callbacks
#     )

#     plot_training_history(history)

# def plot_training_history(history):
#     plt.figure(figsize=(12, 4))

#     plt.subplot(1, 2, 1)
#     plt.plot(history.history['accuracy'], label='Train Acc')
#     plt.plot(history.history['val_accuracy'], label='Val Acc')
#     plt.xlabel('Epoch')
#     plt.ylabel('Accuracy')
#     plt.legend()
#     plt.title('Accuracy')

#     plt.subplot(1, 2, 2)
#     plt.plot(history.history['loss'], label='Train Loss')
#     plt.plot(history.history['val_loss'], label='Val Loss')
#     plt.xlabel('Epoch')
#     plt.ylabel('Loss')
#     plt.legend()
#     plt.title('Loss')

#     plt.tight_layout()
#     plt.show()
    
# def train_img_emotion_model():
#     train_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/train'
#     test_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/test'

#     # Tạo data generators
#     print("🔄 Creating data generators...")
#     train_gen, test_gen = create_data_generators(train_dir, test_dir)

#     # Xây dựng model
#     print("🔨 Building the emotion model...")
#     model = build_improved_emotion_model(input_shape=(48, 48, 1), num_classes=7)
#     model.summary()
    
#     model_path = 'D:/Deep_Learning/main/pythonAPI/emotion_model/img_model/img_emotion_model'  # Lưu model dưới dạng thư mục (Keras 3.x+)

#     # Train model
#     print("🚀 Training the model...")
#     train_model(model, train_gen, test_gen, epochs=50, model_dir=model_path)
#     print("✅ Training completed. Model saved in 'models' directory.")

#     # Lưu model ra folder đúng chuẩn Keras 3.x+
#     print(f"💾 Saving model to folder: {model_path}")
#     model.save(model_path)
#     print(f"✅ Model folder saved at: {model_path}")