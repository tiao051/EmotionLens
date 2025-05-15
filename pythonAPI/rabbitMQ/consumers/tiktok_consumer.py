import json
import os
import asyncio
from tiktokAPI.tiktokcrawldata import extract_video_id, get_comments
from tiktokAPI.tiktokcrawlaudio import download_audio_from_tiktok
from tiktokAPI.tiktokcrawlimg import download_imgframe_tiktok_video, extract_frame
from config import TIKTOK_API_CONFIG

async def process_tiktok_message(file_id, url_content):
    try:
        print(f"Processing TikTok message for ID: {file_id}")
        video_id = extract_video_id(url_content)
        if not video_id:
            print(f"❌ Không thể lấy video_id từ URL: {url_content}")
            return

        print(f"Extracted video ID: {video_id}")

        # Crawl comments
        ms_token = TIKTOK_API_CONFIG["ms_token"]
        output_path = os.path.join(TIKTOK_API_CONFIG["save_csv_path"], f"comments_{video_id}.csv")
        await get_comments(video_id, ms_token, output_path)
        print(f"✅ Successfully crawled comments for video ID {video_id}")

    except Exception as e:
        print(f"❌ Error processing TikTok comments for ID {file_id}: {e}")

async def procees_tiktok_frame_img(file_id, url_content):
    try:
        print(f"Processing TikTok frame image for ID: {file_id}")

        video_path = download_imgframe_tiktok_video(url_content)
        if not video_path:
            print(f"❌ Không thể tải video từ URL: {url_content}")
            return None 

        frame_dir = extract_frame(video_path)
        if not frame_dir:
            print(f"❌ Không thể trích xuất frame từ video: {video_path}")
            return None  

        print(f"✅ Frame image for video ID {file_id} has been processed successfully.")
        return frame_dir

    except Exception as e:
        print(f"❌ Failed to process frame image for video ID {file_id}. Error: {e}")
        return None  

async def process_tiktok_audio(file_id, url_content):
    try:
        print(f"Processing TikTok audio for ID: {file_id}")
        download_audio_from_tiktok(url_content)
        print(f"✅ Audio for video ID {file_id} has been downloaded successfully.")
    except Exception as e:
        print(f"❌ Failed to download audio for video ID {file_id}. Error: {e}")

async def process_tiktok_callbacks(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    url_content = message.get("Url")

    if not url_content:
        print(f"❌ Missing URL for ID: {file_id}")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    print(f"Received ID: {file_id}")
    print(f"Received URL: {url_content}")

    # Tạo các task xử lý song song
    tasks = [
        asyncio.create_task(process_tiktok_message(file_id, url_content)),
        asyncio.create_task(process_tiktok_audio(file_id, url_content)),    
        asyncio.create_task(procees_tiktok_frame_img(file_id, url_content)) 
    ]

    await asyncio.gather(*tasks)

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"✅ Tiktok URL with ID: {file_id} processed and acknowledged.")
