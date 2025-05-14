def train_efficientnet_emotion_model():
    from emotion_model.efficientNet_model.build import build_finetune_efficientnet
    from tensorflow.keras.applications.efficientnet import preprocess_input
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
    import os

    train_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/train'
    test_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/test'

    print("🔄 Creating data generators for EfficientNet (RGB, 224x224)...")
    train_datagen = ImageDataGenerator(
        preprocessing_function=preprocess_input,
        rotation_range=25,
        width_shift_range=0.25,
        height_shift_range=0.25,
        shear_range=0.18,
        zoom_range=0.18,
        brightness_range=(0.8, 1.2),
        horizontal_flip=True,
        fill_mode='nearest'
    )
    test_datagen = ImageDataGenerator(preprocessing_function=preprocess_input)
    train_gen = train_datagen.flow_from_directory(
        train_dir,
        target_size=(224, 224),
        color_mode='rgb',
        batch_size=64,
        class_mode='categorical',
        shuffle=True
    )
    test_gen = test_datagen.flow_from_directory(
        test_dir,
        target_size=(224, 224),
        color_mode='rgb',
        batch_size=64,
        class_mode='categorical',
        shuffle=False
    )

    print("🔨 Building EfficientNetB0 for emotion classification...")
    model = build_finetune_efficientnet(input_shape=(224, 224, 3), num_classes=7)
    model.summary()

    model_path = 'D:/Deep_Learning/main/pythonAPI/emotion_model/efficientNet_model/efficientnet_emotion_model'  # Lưu model dưới dạng thư mục

    print("🚀 Training EfficientNet model...")
    callbacks = [
        EarlyStopping(monitor='val_accuracy', patience=15, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_accuracy', factor=0.2, patience=7, min_lr=1e-6)
    ]
    model.fit(
        train_gen,
        epochs=100,
        validation_data=test_gen,
        callbacks=callbacks
    )
    print(f"✅ Training completed. Model saved in: {model_path}")

    print(f"💾 Saving EfficientNet model to folder: {model_path}")
    model.save(model_path)
    print(f"✅ Model folder saved at: {model_path}")