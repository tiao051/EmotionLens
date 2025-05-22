def train_efficientnet_emotion_model():
    import os
    from tensorflow.keras.applications.efficientnet import preprocess_input
    from tensorflow.keras.preprocessing.image import ImageDataGenerator
    from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
    from emotion_model.efficientNet_model.build import build_finetune_efficientnet

    # ✅ Đường dẫn dữ liệu
    train_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/train'
    test_dir = 'D:/Deep_Learning/dataSet/trainData/fer2013/test'

    # ✅ Đường dẫn lưu file model (.keras)
    model_path = 'D:/Deep_Learning/main/pythonAPI/emotion_model/efficientNet_model'

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
    num_classes = len(train_gen.class_indices)
    model = build_finetune_efficientnet(input_shape=(224, 224, 3), num_classes=num_classes)
    model.summary()

    print("🚀 Training EfficientNet model...")
    callbacks = [
        EarlyStopping(monitor='val_accuracy', patience=15, restore_best_weights=True),
        ReduceLROnPlateau(monitor='val_accuracy', factor=0.2, patience=7, min_lr=1e-6),
        ModelCheckpoint(filepath=model_path, monitor='val_accuracy', save_best_only=True)
    ]

    model.fit(
        train_gen,
        epochs=1,
        validation_data=test_gen,
        callbacks=callbacks
    )

    # ✅ Lưu file cuối cùng (nếu muốn)  
    print(f"💾 Saving final model to file: {model_path}")
    model.save(model_path)
    print(f"✅ Model saved at: {model_path}")
    print("✅ Training completed successfully!")
