import json
import os
from tiktokAPI.tiktokcrawldata import extract_video_id, get_comments 
from config import TIKTOK_API_CONFIG

async def callback_tiktok(ch, method, properties, body):
    message = json.loads(body)
    file_id = message.get("Id")
    url_content = message.get("Url")
    
    if url_content:
        print(f"Received ID: {file_id}")
        print(f"Received URL: {url_content}")
        
        video_id = extract_video_id(url_content)
        if not video_id:
            print("❌ Không thể lấy video_id từ URL.")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        print(f"Extracted video ID: {video_id}")
        
        ms_token = TIKTOK_API_CONFIG["ms_token"]
        output_path = os.path.join(TIKTOK_API_CONFIG["save_csv_path"], f"comments_{video_id}.csv")
        
        try:
            await get_comments(video_id, ms_token, output_path)
            print(f"Successfully crawled comments for video ID {video_id}")
        except Exception as e:
            print(f"Error crawling TikTok data for video ID {video_id}: {e}")

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"Tiktok URL with ID: {file_id} processed and acknowledged.")
    