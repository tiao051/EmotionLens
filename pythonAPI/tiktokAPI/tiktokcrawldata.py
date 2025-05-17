from TikTokApi import TikTokApi
import os
import csv
import re
import emoji
from datetime import datetime
from rabbitMQ.producers.text_producer import TextQueueProducer

async def get_comments(video_id: str, ms_token: str, output_dir: str = "comments_export"):
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{video_id}_{now}.csv")

    producer = TextQueueProducer(queue_name="comment_queue")

    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=5,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=True
        )
        video = api.video(id=video_id)

        with open(output_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["author", "text"])  # Ghi header

            index = 0
            async for comment in video.comments(count=1000):
                author = comment.author.username
                text = normalizeComment(comment.text)
                writer.writerow([author, text])

                message = {
                    "video_id": video_id,
                    "author": author,
                    "text": text,
                    "isFinal": False
                }

                try:
                    producer.send_comment_to_queue(message)
                    index += 1
                except Exception as e:
                    print(f"❌ Lỗi gửi comment #{index}: {e}")

    # Gửi message cuối cùng
    final_msg = {
        "video_id": video_id,
        "isFinal": True
    }
    try:
        producer.send_comment_to_queue(final_msg)
        print(f"✅ Gửi message cuối cùng báo hiệu kết thúc.")
    except Exception as e:
        print(f"❌ Lỗi gửi message cuối cùng: {e}")
    
    producer.close()
    print(f"✅ Đã crawl và gửi {index} comment. File lưu tại: {output_path}")

def clean_whitespace(text):
    return ' '.join(text.strip().split())

def remove_emoji(text):
    return emoji.replace_emoji(text, replace='')

def remove_special_characters(text):
    return re.sub(r"[^\w\sÀ-ỹà-ỹ]", "", text)

def normalizeComment(text):
    text = text.lower()
    text = clean_whitespace(text)
    text = remove_emoji(text)
    text = remove_special_characters(text)

    return text

def extract_video_id(tiktok_url):
    match = re.search(r'/video/(\d+)', tiktok_url)
    if not match:
        match = re.search(r'/photo/(\d+)', tiktok_url)
    return match.group(1) if match else None