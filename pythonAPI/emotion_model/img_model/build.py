from tensorflow.keras.models import Sequential # type: ignore
from tensorflow.keras.layers import Conv2D, MaxPooling2D, GlobalAveragePooling2D, Dense, Dropout, BatchNormalization # type: ignore
from tensorflow.keras.optimizers import Adam # type: ignore
from tensorflow.keras.losses import CategoricalCrossentropy # type: ignore
from tensorflow.keras.regularizers import l2 # type: ignore

def build_improved_emotion_model(input_shape=(48, 48, 1), num_classes=7):
    model = Sequential()

    # Block 1: Initial Convolutional Block
    model.add(Conv2D(64, (3, 3), padding='same', activation='relu', input_shape=input_shape, kernel_regularizer=l2(0.001)))
    model.add(BatchNormalization())  # Batch Normalization to stabilize learning
    model.add(MaxPooling2D(pool_size=(2, 2)))  # Max pooling for downsampling

    # Block 2: Second Convolutional Block
    model.add(Conv2D(128, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(0.001)))
    model.add(BatchNormalization())  # Batch Normalization for regularization
    model.add(MaxPooling2D(pool_size=(2, 2)))  # Max pooling for dimensionality reduction

    # Block 3: Third Convolutional Block with Dropout
    model.add(Conv2D(256, (3, 3), padding='same', activation='relu', kernel_regularizer=l2(0.001)))
    model.add(BatchNormalization())  # Batch Normalization for improving generalization
    model.add(MaxPooling2D(pool_size=(2, 2)))  # Pooling layer
    model.add(Dropout(0.3))  # Dropout for regularization to reduce overfitting

    # Classifier Section: Fully Connected Layers
    model.add(GlobalAveragePooling2D())  # Global Average Pooling instead of Flatten to reduce overfitting and parameters
    model.add(Dense(512, activation='relu', kernel_regularizer=l2(0.001)))  # Dense layer with L2 regularization
    model.add(Dropout(0.5))  # Dropout for further regularization
    model.add(Dense(num_classes, activation='softmax'))  # Output layer with softmax activation for multi-class classification

    # Compile the model with label smoothing for better generalization
    model.compile(
        optimizer=Adam(learning_rate=0.0005),  # Lower learning rate for fine-tuning
        loss=CategoricalCrossentropy(label_smoothing=0.1),  # Use label_smoothing in loss
        metrics=['accuracy']  # Track accuracy during training
    )

    return model
