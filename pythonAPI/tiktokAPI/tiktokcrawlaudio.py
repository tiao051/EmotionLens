import yt_dlp
import os
import subprocess

def download_audio_from_tiktok(url):
    output_dir = r"D:\Deep_Learning\dataSet\exportData\pythonExportData\audio_data"
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(id)s.%(ext)s'),
        'noplaylist': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        downloaded_file = os.path.join(output_dir, f"{info['id']}.{info['ext']}")

    if downloaded_file.endswith(".mp4") or downloaded_file.endswith(".webm"):
        mp3_file = downloaded_file.rsplit(".", 1)[0] + ".mp3"

        try:
            subprocess.run([
                r"D:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe",
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

        except subprocess.CalledProcessError as e:
            print(f"❌ Lỗi chuyển đổi MP3: {e}")
    else:
        print(f"✅ Không cần chuyển đổi: {downloaded_file}")

def split_mp3_file(mp3_path, segment_length=10):
    output_dir = os.path.join(os.path.dirname(mp3_path), "segments")
    os.makedirs(output_dir, exist_ok=True)

    command = [
        r"D:\ffmpeg\ffmpeg-7.1.1-essentials_build\bin\ffmpeg.exe",
        "-i", mp3_path,
        "-f", "segment",
        "-segment_time", str(segment_length),
        "-c", "copy",
        os.path.join(output_dir, "output_%03d.mp3")
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Đã cắt file thành các đoạn dài {segment_length} giây.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Lỗi khi cắt file: {e}")
