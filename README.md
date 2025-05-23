# EmotionLens - Hệ thống phân tích cảm xúc đa modal

## Mô tả dự án
EmotionLens là hệ thống phân tích cảm xúc từ nhiều nguồn dữ liệu (text, hình ảnh, audio) trên mạng xã hội (TikTok, YouTube, v.v.), sử dụng các mô hình học sâu hiện đại. Hệ thống gồm backend .NET (Web API & MVC), frontend web đơn giản, và các Python worker xử lý AI.

## Kiến trúc tổng thể
- **Frontend**: HTML5, CSS3, JavaScript, jQuery, Font Awesome
- **Backend**: ASP.NET Core MVC & Web API, RabbitMQ, Newtonsoft.Json
- **AI Service**: Python (Transformers, TensorFlow/Keras, librosa, ...)
- **Message Queue**: RabbitMQ

## Các mô hình AI sử dụng
- **Text**: DistilBERT (transformers) fine-tune phân loại cảm xúc bình luận
- **Image**: EfficientNetB0 (CNN) fine-tune phân loại cảm xúc khuôn mặt
- **Audio**: BiLSTM + Multi-Head Attention trên đặc trưng MFCC

## Hướng dẫn cài đặt

### Điều kiện tiên quyết
- Sau khi đã giải nén file hãy đặt file Deep_Learning ở ngay thư mục ổ D để những phần code đang bị hardcode có thể hoạt động đúng.
- Tương tự, hãy giải nén file ffmpeg.rar và để nó ở ngay thư mục ổ D.

### 1. Chuẩn bị môi trường
- Cài đặt .NET 9.0.100
- Cài đặt Python 3.10.9
- Cài đặt RabbitMQ server

### 2. Cài đặt backend .NET
```sh
cd landingPage/deepLearning
 dotnet restore
 dotnet build
 dotnet run
```
Hoặc lý tưởng hơn:
- Sử dụng Visual Studio cho phần C#
- Run bằng VS.
### 3. Cài đặt Python AI service
```sh
cd pythonAPI
pip install -r requirements.txt
```

### 4. Cấu hình RabbitMQ (Sử dụng thông qua Docker)
- Đảm bảo bạn cài Docker và Docker daemon đang chạy.
- Chủ động pull RabbitMQ về (nếu chưa có) bằng dòng lệnh sau:
docker pull rabbitmq:management (và đảm bảo không trùng tên với các containers cũ).

- Truy cập vào RabbitMQ Web UI:
    - Tài khoản mặc định:
        Username: guest
        Password: guest
    - Vào phần Admin
        Chọn Add a user với username và password: admin
        Trong phần tags set quyền admin
        Chọn Add user
    - Sau đó bấm vào user vừa tạo và set permission cho virtual host
    - Cuối cùng là logout khỏi guest và truy cập lại vào bằng username và password vừa tạo cho admin.

### 5. Chạy Python worker
```sh
cd pythonAPI
python main.py
```
Hoặc lý tưởng hơn:
- Sử dụng VSCode cho phần Python
- Run từ thư mục main.py
### 6. Truy cập giao diện web
- Mở trình duyệt và truy cập: http://localhost:44354 (nếu sử dụng terminal)

## Luồng hoạt động chính
1. User gửi dữ liệu (text, ảnh, audio, hoặc URL TikTok/YouTube) lên web
2. Backend .NET nhận request, xác định loại dữ liệu, gửi message vào queue tương ứng
3. Python worker lắng nghe queue, xử lý bằng mô hình AI phù hợp, trả kết quả về backend
4. Backend trả kết quả cho frontend, hiển thị cho user

## Data set
- FER2013 dataset
- HuggingFace dataset (đã được tái xử lý cho phù hợp với đề tài)

---

Nếu gặp lỗi hoặc cần hỗ trợ, vui lòng liên hệ nhóm phát triển qua gmail: nguyenminhtho0503@gmail.com
