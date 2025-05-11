import yt_dlp
import os

def download_audio_from_tiktok(url):
    output_dir = r"D:\Deep_Learning\dataSet\exportData\pythonExportData\audio_data"
    os.makedirs(output_dir, exist_ok=True)  # Tạo thư mục nếu chưa tồn tại

    # Cấu hình yt-dlp để tải audio mà không cần FFmpeg
    ydl_opts = {
        'format': 'bestaudio/best',  # Tải audio chất lượng cao nhất
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),  # Lưu vào thư mục đã chỉ định
        'noplaylist': True,  # Không tải playlist nếu có
        'postprocessors': [],  # Không sử dụng postprocessor (FFmpeg)
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    print("Audio đã được tải xuống thành công!")


