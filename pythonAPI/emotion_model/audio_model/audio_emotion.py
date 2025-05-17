import os
import numpy as np
import librosa
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
import tensorflow as tf
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import (Input, Conv1D, MaxPooling1D, Dropout,
                                   BatchNormalization, LSTM, Bidirectional,
                                   Dense, LayerNormalization, Add,
                                   MultiHeadAttention, GlobalAveragePooling1D)
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.regularizers import l2
from tensorflow.keras.losses import CategoricalCrossentropy


class AudioFeatureExtractor:
    def __init__(self, n_mfcc=80, max_len=400):
        self.n_mfcc = n_mfcc
        self.max_len = max_len
    
    def extract_mfcc_from_file(self, file_path, augment=False):
        # Đọc file âm thanh
        y, sr = librosa.load(file_path, sr=None)
        
        # Thực hiện data augmentation nếu cần
        if augment:
            y = self._random_augment(y, sr)
        
        # Trích xuất MFCC
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=self.n_mfcc)
        
        # Chuẩn hóa kích thước
        if mfcc.shape[1] < self.max_len:
            # Pad nếu file quá ngắn
            pad_width = self.max_len - mfcc.shape[1]
            mfcc = np.pad(mfcc, ((0,0),(0,pad_width)), mode='constant')
        else:
            # Cắt nếu file quá dài
            mfcc = mfcc[:, :self.max_len]
        
        # Chuyển vị ma trận cho định dạng đầu vào LSTM và normalize
        mfcc = mfcc.T  # shape: (max_len, n_mfcc)
        
        # Chuẩn hóa: trừ mean, chia std theo từng file
        mean = np.mean(mfcc, axis=0, keepdims=True)
        std = np.std(mfcc, axis=0, keepdims=True) + 1e-8
        mfcc_norm = (mfcc - mean) / std
        
        return mfcc_norm
    
    def _augment_speed(self, y, rate=None):
        import random
        if rate is None:
            rate = random.uniform(0.9, 1.1)
        return librosa.effects.time_stretch(y, rate)

    def _augment_pitch(self, y, sr, n_steps=None):
        import random
        if n_steps is None:
            n_steps = random.randint(-2, 2)
        return librosa.effects.pitch_shift(y, sr, n_steps=n_steps)

    def _augment_noise(self, y, noise_level=None):
        import random
        if noise_level is None:
            noise_level = random.uniform(0.001, 0.01)
        noise = np.random.randn(len(y))
        return y + noise_level * noise

    def _random_augment(self, y, sr):
        import random
        # Xác suất mỗi augmentation ~50%
        if random.random() < 0.5:
            y = self._augment_speed(y)
        if random.random() < 0.5:
            y = self._augment_pitch(y, sr)
        if random.random() < 0.5:
            y = self._augment_noise(y)
        return y


class EmotionDataProcessor:
    def __init__(self, feature_extractor=None, emotions=None):
        if feature_extractor is None:
            self.feature_extractor = AudioFeatureExtractor()
        else:
            self.feature_extractor = feature_extractor
            
        if emotions is None:
            self.emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad']
        else:
            self.emotions = emotions
            
        self.label_encoder = LabelEncoder()
    
    def extract_features_from_directory(self, audio_root, output_features=None, output_labels=None):
        import tqdm
        features = []
        labels = []

        for emotion in self.emotions:
            emotion_dir = os.path.join(audio_root, emotion)
            if not os.path.exists(emotion_dir):
                continue
                
            files = [f for f in os.listdir(emotion_dir) if f.endswith('.wav') or f.endswith('.mp3')]
            
            for f in tqdm.tqdm(files, desc=f"Extracting {emotion}"):
                file_path = os.path.join(emotion_dir, f)
                try:
                    # Đặc trưng gốc
                    mfcc_seq = self.feature_extractor.extract_mfcc_from_file(file_path)
                    features.append(mfcc_seq)
                    labels.append(emotion)
                    
                    # Augmentation 1
                    mfcc_aug1 = self.feature_extractor.extract_mfcc_from_file(file_path, augment=True)
                    features.append(mfcc_aug1)
                    labels.append(emotion)
                    
                    # Có thể thêm augmentation 2, 3... nếu muốn
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")
        
        features = np.array(features)  # shape: (num_samples, max_len, n_mfcc)
        labels = np.array(labels)
        
        # Lưu file nếu có chỉ định đường dẫn
        if output_features is not None:
            np.save(output_features, features)
            
        if output_labels is not None:
            np.save(output_labels, labels)
            
        print(f"Done! Extracted {len(features)} samples with shape {features.shape}")
        return features, labels
    
    def prepare_training_data(self, features, labels, test_size=0.2, random_state=42):
        # Mã hóa nhãn
        y_encoded = self.label_encoder.fit_transform(labels)
        y_cat = to_categorical(y_encoded)
        
        # Chia dữ liệu
        X_train, X_test, y_train, y_test = train_test_split(
            features, y_cat, test_size=test_size, stratify=y_cat, random_state=random_state
        )
        
        # Tính class weights
        y_flat = np.argmax(y_cat, axis=1)
        class_weights = compute_class_weight('balanced', classes=np.unique(y_flat), y=y_flat)
        class_weight_dict = dict(enumerate(class_weights))
        
        return X_train, X_test, y_train, y_test, class_weight_dict


class EmotionRecognitionModel:
    def __init__(self, input_shape=None, num_classes=6):
        self.input_shape = input_shape
        self.num_classes = num_classes
        self.model = None
        self.history = None
        
    def build_bilstm_mha_model(self):
        """
        Xây dựng mô hình BiLSTM kết hợp với Multi-Head Attention
        
        Returns:
            Model: Mô hình đã xây dựng
        """
        if self.input_shape is None:
            raise ValueError("input_shape must be specified")
            
        # Đầu vào
        inp = Input(shape=self.input_shape)
        
        # Khối tích chập 1
        x = Conv1D(64, kernel_size=5, activation='relu', padding='same', kernel_regularizer=l2(1e-4))(inp)
        x = BatchNormalization()(x)
        x = MaxPooling1D(pool_size=2)(x)
        x = Dropout(0.15)(x)
        
        # Khối tích chập 2
        x = Conv1D(128, kernel_size=3, activation='relu', padding='same', kernel_regularizer=l2(1e-4))(x)
        x = BatchNormalization()(x)
        x = MaxPooling1D(pool_size=2)(x)
        x = Dropout(0.2)(x)
        
        # Khối BiLSTM
        x = Bidirectional(LSTM(64, return_sequences=True))(x)
        x = Dropout(0.2)(x)
        
        # Khối Multi-Head Attention
        attn = MultiHeadAttention(num_heads=4, key_dim=64)(x, x)
        x = Add()([x, attn])
        x = LayerNormalization()(x)
        
        # Global Pooling
        x = GlobalAveragePooling1D()(x)
        
        # Khối Fully Connected
        x = Dense(64, activation='relu', kernel_regularizer=l2(1e-4))(x)
        x = Dropout(0.3)(x)
        x = Dense(32, activation='relu', kernel_regularizer=l2(1e-4))(x)
        x = Dropout(0.2)(x)
        
        # Output layer
        output = Dense(self.num_classes, activation='softmax')(x)
        
        # Tạo mô hình
        self.model = Model(inputs=inp, outputs=output)
        
        # Biên dịch mô hình
        self.model.compile(
            optimizer='adam',
            loss=CategoricalCrossentropy(label_smoothing=0.1),
            metrics=['accuracy']
        )
        
        return self.model
    
    def train(self, X_train, y_train, X_test, y_test, class_weight_dict=None, 
              epochs=60, batch_size=32, patience=6):
        """
        Huấn luyện mô hình
        
        Args:
            X_train (np.ndarray): Dữ liệu huấn luyện
            y_train (np.ndarray): Nhãn huấn luyện
            X_test (np.ndarray): Dữ liệu kiểm tra
            y_test (np.ndarray): Nhãn kiểm tra
            class_weight_dict (dict): Trọng số cho các lớp
            epochs (int): Số epoch tối đa
            batch_size (int): Kích thước batch
            patience (int): Số epoch tối đa không cải thiện
            
        Returns:
            History: Lịch sử huấn luyện
        """
        # Kiểm tra mô hình đã được xây dựng chưa
        if self.model is None:
            if self.input_shape is None:
                self.input_shape = X_train.shape[1:]
                self.num_classes = y_train.shape[1]
            self.build_bilstm_mha_model()
        
        # Callbacks
        early_stop = EarlyStopping(
            monitor='val_accuracy',
            patience=patience,
            restore_best_weights=True,
            mode='max'
        )
        
        reduce_lr = ReduceLROnPlateau(
            monitor='val_accuracy',
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            mode='max'
        )
        
        # Huấn luyện mô hình
        self.history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_test, y_test),
            callbacks=[early_stop, reduce_lr],
            class_weight=class_weight_dict
        )
        
        return self.history
    
    def evaluate(self, X_test, y_test, label_names=None):
        """
        Đánh giá mô hình
        
        Args:
            X_test (np.ndarray): Dữ liệu kiểm tra
            y_test (np.ndarray): Nhãn kiểm tra (one-hot encoding)
            label_names (list): Tên các lớp
            
        Returns:
            tuple: (loss, accuracy, report) - Độ lỗi, độ chính xác và báo cáo phân loại chi tiết
        """
        # Đánh giá
        loss, acc = self.model.evaluate(X_test, y_test)
        print(f"\n🎯 Test accuracy: {acc:.2%}")
        
        # Dự đoán và so sánh
        y_pred = np.argmax(self.model.predict(X_test), axis=1)
        y_true = np.argmax(y_test, axis=1)
        
        # Báo cáo phân loại
        report = classification_report(y_true, y_pred, target_names=label_names, output_dict=True)
        print("\n📊 Classification report:\n")
        print(classification_report(y_true, y_pred, target_names=label_names))
        
        return loss, acc, report
    
    def save_model(self, model_path):
        """
        Lưu mô hình
        
        Args:
            model_path (str): Đường dẫn lưu mô hình
        """
        if self.model is None:
            raise ValueError("Model has not been built or trained")
            
        self.model.save(model_path)
        print(f"✅ Model saved to {model_path}")
    
    def load_model(self, model_path):
        """
        Tải mô hình đã lưu
        
        Args:
            model_path (str): Đường dẫn tới mô hình
            
        Returns:
            Model: Mô hình đã tải
        """
        self.model = load_model(model_path)
        return self.model
    
    def predict(self, features):
        """
        Dự đoán cảm xúc từ đặc trưng
        
        Args:
            features (np.ndarray): Đặc trưng MFCC đã chuẩn hóa
            
        Returns:
            np.ndarray: Xác suất các lớp cảm xúc
        """
        if self.model is None:
            raise ValueError("Model has not been built or loaded")
            
        # Ensure features have the right shape (add batch dimension if needed)
        if len(features.shape) == 2:
            features = np.expand_dims(features, axis=0)
            
        return self.model.predict(features)
    
    def plot_training_history(self, save_path=None):
        """
        Vẽ biểu đồ lịch sử huấn luyện
        
        Args:
            save_path (str, optional): Đường dẫn lưu biểu đồ
        """
        if self.history is None:
            raise ValueError("Model has not been trained")
            
        plt.figure(figsize=(12, 5))
        
        # Đồ thị loss
        plt.subplot(1, 2, 1)
        plt.plot(self.history.history['loss'], label='Train loss')
        plt.plot(self.history.history['val_loss'], label='Val loss')
        plt.title('Loss per Epoch')
        plt.legend()
        
        # Đồ thị accuracy
        plt.subplot(1, 2, 2)
        plt.plot(self.history.history['accuracy'], label='Train acc')
        plt.plot(self.history.history['val_accuracy'], label='Val acc')
        plt.title('Accuracy per Epoch')
        plt.legend()
        
        plt.tight_layout()
        
        if save_path is not None:
            plt.savefig(save_path)
            print(f"✅ Training history plot saved to {save_path}")
            
        plt.show()


class EmotionPredictorApp:
    """
    Lớp ứng dụng dự đoán cảm xúc
    """
    def __init__(self, model_path, labels_path):
        """
        Khởi tạo ứng dụng dự đoán cảm xúc
        
        Args:
            model_path (str): Đường dẫn tới mô hình đã huấn luyện
            labels_path (str): Đường dẫn tới file nhãn
        """
        # Tạo trình trích xuất đặc trưng
        self.feature_extractor = AudioFeatureExtractor()
        
        # Tải mô hình
        self.model = EmotionRecognitionModel()
        self.model.load_model(model_path)
        
        # Tạo và huấn luyện LabelEncoder
        self.labels = np.load(labels_path)
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(self.labels)
    
    def predict_from_file(self, audio_path):
        """
        Dự đoán cảm xúc từ file âm thanh
        
        Args:
            audio_path (str): Đường dẫn tới file âm thanh
            
        Returns:
            tuple: (emotion, probs) - Cảm xúc dự đoán và xác suất các lớp
        """
        # Trích xuất đặc trưng
        features = self.feature_extractor.extract_mfcc_from_file(audio_path)
        
        # Dự đoán
        probs = self.model.predict(features)[0]
        
        # Lấy class có xác suất cao nhất
        pred_idx = np.argmax(probs)
        
        # Chuyển đổi từ index về nhãn cảm xúc
        emotion = self.label_encoder.inverse_transform([pred_idx])[0]
        
        return emotion, probs
    
    def run_gui(self):
        """
        Chạy giao diện người dùng đơn giản
        """
        import tkinter as tk
        from tkinter import filedialog, messagebox
        
        # Khởi tạo giao diện
        root = tk.Tk()
        root.withdraw()
        
        # Hiển thị hộp thoại chọn file
        file_path = filedialog.askopenfilename(
            title="Chọn file audio để phân tích cảm xúc",
            filetypes=[("Audio files", "*.wav *.mp3")]
        )
        
        if not file_path:
            print("Không có file nào được chọn.")
            return
            
        try:
            # Dự đoán cảm xúc
            emotion, probs = self.predict_from_file(file_path)
            
            # Tạo nội dung thông báo kết quả
            msg = f"Dự đoán cảm xúc: {emotion}\n\nXác suất từng lớp:\n"
            for i, label in enumerate(self.label_encoder.classes_):
                msg += f"{label}: {probs[i]:.2%}\n"
                
            # Hiển thị kết quả
            messagebox.showinfo("Kết quả phân tích cảm xúc", msg)
            print(msg)
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể phân tích file này!\n{e}")
            print(f"Lỗi: {e}")
