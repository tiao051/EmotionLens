import yt_dlp
import os
import subprocess
import math
from datetime import datetime

FFMPEG_PATH = r"D:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe"
AUDIO_OUTPUT_DIR = r"D:\Deep_Learning\dataSet\exportData\pythonExportData\audio_data"

def download_audio_from_tiktok(url, max_segments=10):
    # Tạo thư mục chính nếu chưa có
    os.makedirs(AUDIO_OUTPUT_DIR, exist_ok=True)

    # Tạo thư mục con theo thời gian
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = os.path.join(AUDIO_OUTPUT_DIR, timestamp)
    os.makedirs(session_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(session_dir, '%(id)s.%(ext)s'),
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        video_id = info['id']
        duration = info.get('duration', 0)
        downloaded_file = os.path.join(session_dir, f"{video_id}.{info['ext']}")

    # Tính độ dài từng đoạn sao cho không vượt quá max_segments
    base_segment = choose_segment_length(duration)
    segment_length = max(base_segment, math.ceil(duration / max_segments)) if duration > 0 else base_segment

    print(f"ℹ️ Video dài {duration}s → mỗi đoạn dài {segment_length}s (≤ {max_segments} đoạn)")

    if downloaded_file.endswith(".mp4") or downloaded_file.endswith(".webm"):
        mp3_file = os.path.join(session_dir, f"{video_id}.mp3")

        try:
            subprocess.run([
                FFMPEG_PATH,
                "-i", downloaded_file,
                "-vn",
                "-ab", "192k",
                "-ar", "44100",
                "-y",
                mp3_file
            ], check=True)

            print(f"✅ Đã chuyển thành MP3: {mp3_file}")
            os.remove(downloaded_file)
            print(f"🗑️ Đã xóa file gốc: {downloaded_file}")

            segment_folder = os.path.join(session_dir, "segments")
            split_mp3_file(mp3_file, segment_length=segment_length, folder_path=segment_folder, video_id=video_id)

        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi chuyển đổi MP3: {e}")
    else:
        print(f"✅ Không cần chuyển đổi: {downloaded_file}")

def choose_segment_length(duration):
    """Chọn độ dài đoạn mặc định theo thời lượng."""
    if duration <= 30:
        return 5
    elif duration <= 90:
        return 10
    elif duration <= 300:
        return 15
    elif duration <= 600:
        return 30
    else:
        return 60

def split_mp3_file(mp3_path, segment_length=10, folder_path="segments", video_id="video"):
    from rabbitMQ.producers.audio_section_producer import AudioSectionProducer  

    os.makedirs(folder_path, exist_ok=True)
    output_template = os.path.join(folder_path, f"{video_id}_sec%01d.mp3")

    command = [
        FFMPEG_PATH,
        "-i", mp3_path,
        "-f", "segment",
        "-segment_time", str(segment_length),
        "-c", "copy",
        output_template
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Đã cắt thành các đoạn trong: '{folder_path}' với định dạng '{video_id}_secX.mp3'")

        # Gửi từng đường dẫn section lên RabbitMQ
        producer = AudioSectionProducer()
        for idx, filename in enumerate(sorted(os.listdir(folder_path))):
            if filename.endswith(".mp3") and filename.startswith(f"{video_id}_sec"):
                full_path = os.path.abspath(os.path.join(folder_path, filename))
                producer.send_section_path(file_path=full_path, video_id=video_id, section_index=idx)
        producer.close()

    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi cắt file: {e}")

