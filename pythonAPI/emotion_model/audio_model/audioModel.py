import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Model
from tensorflow.keras.layers import (Input, Conv1D, MaxPooling1D, Dropout,
                                     BatchNormalization, LSTM, Bidirectional,
                                     Dense, Flatten, MultiHeadAttention)
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.regularizers import l2

###############################################################
# 1. Tự động tải file đặc trưng và nhãn từ Google Drive nếu chưa có
###############################################################
try:
    import gdown
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', 'gdown'])
    import gdown

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
###############################################################
# 2. Đường dẫn tương đối
###############################################################
FEATURES_PATH = os.path.join(SCRIPT_DIR, "..", "..", "dataSet", "CREMA-D", "crema_d_features_seq.npy")
LABELS_PATH = os.path.join(SCRIPT_DIR, "..", "..", "dataSet", "CREMA-D", "crema_d_labels_seq.npy")
FEATURES_PATH = os.path.normpath(FEATURES_PATH)
LABELS_PATH = os.path.normpath(LABELS_PATH)

###############################################################
# 3. File ID trên Google Drive (cần thay đúng ID nếu đổi file)
###############################################################
FEATURES_ID = '1Y9agbebhyNykWEFFrbjdfUT7uirooibW'
LABELS_ID = '1b6-CnIFD1yaK-gvti_uw5jfBf0PkBarC'


# Hàm tải file nếu chưa có
def download_if_not_exists(path, file_id):
    dir_path = os.path.dirname(path)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    if not os.path.exists(path):
        url = f'https://drive.google.com/uc?id={file_id}'
        print(f"Downloading {path} from Google Drive...")
        gdown.download(url, path, quiet=False)


# Tải file đặc trưng và nhãn nếu chưa có
download_if_not_exists(FEATURES_PATH, FEATURES_ID)
download_if_not_exists(LABELS_PATH, LABELS_ID)



###############################################################
# 4. Load đặc trưng MFCC & nhãn (đã trích xuất sẵn)
###############################################################
X = np.load(FEATURES_PATH)  # shape: (num_samples, max_len, n_mfcc)
y = np.load(LABELS_PATH)    # shape: (num_samples,)


###############################################################
# 5. Encode nhãn (label encoding + one-hot)
###############################################################
le = LabelEncoder()
y_encoded = le.fit_transform(y)
y_cat = to_categorical(y_encoded)


###############################################################
# 6. Chia tập train/test (giữ tỉ lệ nhãn đều)
###############################################################
X_train, X_test, y_train, y_test = train_test_split(
    X, y_cat, test_size=0.2, stratify=y_cat, random_state=42
)


###############################################################
# 7. Tính class_weight để giảm mất cân bằng nhãn
###############################################################
y_flat = np.argmax(y_cat, axis=1)
class_weights = compute_class_weight('balanced', classes=np.unique(y_flat), y=y_flat)
class_weight_dict = dict(enumerate(class_weights))



###############################################################
###############################################################
# 8. Xây dựng model CNN + BiLSTM + MultiHeadAttention (cải tiến)
###############################################################
###############################################################
input_shape = X.shape[1:]
inp = Input(shape=input_shape)


# 3 lớp Conv1D trích xuất đặc trưng cục bộ
x = Conv1D(32, kernel_size=5, activation='relu', padding='same', kernel_regularizer=l2(1e-4))(inp)
x = BatchNormalization()(x)
x = MaxPooling1D(pool_size=2)(x)
x = Dropout(0.15)(x)

x = Conv1D(64, kernel_size=3, activation='relu', padding='same', kernel_regularizer=l2(1e-4))(x)
x = BatchNormalization()(x)
x = MaxPooling1D(pool_size=2)(x)
x = Dropout(0.15)(x)

x = Conv1D(128, kernel_size=3, activation='relu', padding='same', kernel_regularizer=l2(1e-4))(x)
x = BatchNormalization()(x)
x = MaxPooling1D(pool_size=2)(x)
x = Dropout(0.2)(x)

# 2 lớp BiLSTM để học thông tin chuỗi thời gian
x = Bidirectional(LSTM(32, return_sequences=True))(x)
x = Dropout(0.2)(x)
x = Bidirectional(LSTM(16, return_sequences=True))(x)
x = Dropout(0.2)(x)

# MultiHeadAttention (cải tiến so với Attention truyền thống)
# Số head = 4, key_dim = 32 (có thể điều chỉnh)
attn = MultiHeadAttention(num_heads=4, key_dim=32)(x, x)
x = Flatten()(attn)

# Dense head phân loại
x = Dense(64, activation='relu', kernel_regularizer=l2(1e-4))(x)
x = Dropout(0.3)(x)
x = Dense(32, activation='relu', kernel_regularizer=l2(1e-4))(x)
x = Dropout(0.2)(x)

output = Dense(y_cat.shape[1], activation='softmax')(x)



###############################################################
# 9. Khởi tạo và compile model
###############################################################
model = Model(inputs=inp, outputs=output)
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])



###############################################################
# 10. Callback chống overfit và tối ưu learning rate
###############################################################
early_stop = EarlyStopping(monitor='val_accuracy', patience=6, restore_best_weights=True, mode='max')
reduce_lr = ReduceLROnPlateau(monitor='val_accuracy', factor=0.5, patience=2, min_lr=1e-6, mode='max')



###############################################################
# 11. Huấn luyện model
###############################################################
history = model.fit(
    X_train, y_train,
    epochs=60,
    batch_size=32,
    validation_data=(X_test, y_test),
    callbacks=[early_stop, reduce_lr],
    class_weight=class_weight_dict
)

y_pred = np.argmax(model.predict(X_test), axis=1)
y_true = np.argmax(y_test, axis=1)



###############################################################
# 12. Đánh giá, báo cáo, lưu model và vẽ biểu đồ loss/accuracy
###############################################################
import matplotlib.pyplot as plt

loss, acc = model.evaluate(X_test, y_test)
print(f"\n🎯 Test accuracy: {acc:.2%}")

# Dự đoán và in classification report
y_pred = np.argmax(model.predict(X_test), axis=1)
y_true = np.argmax(y_test, axis=1)
print("\n📊 Classification report:\n")
print(classification_report(y_true, y_pred, target_names=le.classes_))

# Lưu model
MODEL_OUT = os.path.join(SCRIPT_DIR, "..", "..", "crema_d_audio_emotion_bilstm_attention.h5")
MODEL_OUT = os.path.normpath(MODEL_OUT)
model.save(MODEL_OUT)
print(f"✅ Model saved to {MODEL_OUT}")

# Vẽ biểu đồ loss/accuracy
plt.figure(figsize=(12,5))
plt.subplot(1,2,1)
plt.plot(history.history['loss'], label='Train loss')
plt.plot(history.history['val_loss'], label='Val loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Loss per epoch')
plt.legend()

plt.subplot(1,2,2)
plt.plot(history.history['accuracy'], label='Train acc')
plt.plot(history.history['val_accuracy'], label='Val acc')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Accuracy per epoch')
plt.legend()

plt.tight_layout()
plt.savefig(os.path.join(SCRIPT_DIR, '..', '..', 'train_history_plot.png'))
plt.show()