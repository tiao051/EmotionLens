import yt_dlp
import os
import subprocess

def download_imgframe_tiktok_video(url):
    output_dir = r"D:\Deep_Learning\dataSet\exportData\pythonExportData\img_data"
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestvideo+bestaudio/best', 
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'), 
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)  
        downloaded_file = os.path.join(output_dir, f"{info['id']}.{info['ext']}")
        print(f"✅ Video đã được tải xuống: {downloaded_file}")
        return downloaded_file
    
def extract_frame(video_path):
    output_dir = r"D:\Deep_Learning\dataSet\exportData\pythonExportData\img_data"
    os.makedirs(output_dir, exist_ok=True)
    try:
        os.makedirs(output_dir, exist_ok=True)

        command = [
            r"D:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe",  # Đường dẫn đến FFmpeg
            "-i", video_path,  # Đường dẫn video đầu vào
            os.path.join(output_dir, "frame_%04d.jpg")  # Đường dẫn lưu các frame
        ]

        subprocess.run(command, check=True)
        print(f"✅ Tất cả các frame đã được trích xuất vào: {output_dir}")
        return output_dir
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi trích xuất frame: {e}")
        return None
    except Exception as e:
        print(f"❌ Lỗi không xác định: {e}")
        return None