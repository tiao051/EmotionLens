import math
import yt_dlp
import os
import cv2
from datetime import datetime
from tiktokAPI.tiktokcrawldata import extract_video_id
from rabbitMQ.producers.frame_producer import FrameQueueProducer

def download_imgframe_tiktok_video(url):
    # Tạo folder riêng cho mỗi video theo ngày giờ hiện tại
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_dir = os.path.join(r"D:\Deep_Learning\dataSet\exportData\pythonExportData\img_data", f"video_{now}")
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
    
def extract_frame(video_path, url_content, output_dir=None):
    print(f"ℹ️ Đường dẫn video: {url_content}")
    video_id = extract_video_id(url_content)
    print(f"🎞️ Đang trích xuất frame từ video ID: {video_id}")
    # Nếu chưa truyền output_dir thì lấy cùng folder với video
    if output_dir is None:
        output_dir = os.path.dirname(video_path)
    os.makedirs(output_dir, exist_ok=True)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = int(total_frames / fps)
    print(f"🎞️ Video dài khoảng: {duration} giây")

    if duration <= 5:
        frame_per_s = 3
    elif duration <= 15:
        frame_per_s = 2
    else:   
        frame_per_s = 1
    
    interval = int(fps / frame_per_s) if frame_per_s > 0 else int(fps)
    count = 0
    saved = 0
    total_to_save = math.ceil(total_frames / interval)

    # Tạo producer 1 lần, gửi nhiều frame
    producer = FrameQueueProducer(queue_name="fps_queue")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if count % interval == 0:
            filename = os.path.join(output_dir, f"frame_{saved:04d}.jpg")
            cv2.imwrite(filename, frame)
            
            is_final = (saved == total_to_save - 1)
            
            # Gửi frame lên queue ngay khi lưu xong
            try:
                if is_final == True:
                    print(f"✅ Gửi frame cuối cùng {filename} lên queue")
                producer.send_frame_to_queue(filename, video_id=video_id, is_final=is_final)
            except Exception as e:
                print(f"❌ Lỗi gửi frame {filename} lên queue: {e}")
            saved += 1
        count += 1

    cap.release()
    producer.close()
    print(f"✅ Trích xuất {saved} frame vào: {output_dir}")
    return output_dir