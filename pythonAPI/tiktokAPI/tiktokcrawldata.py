from TikTokApi import TikTokApi
import os
import csv
import re
import emoji
from rabbitMQ.producers.comments_producer import CommentQueueProducer

async def get_comments(video_id: str, ms_token: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True) 

    producer = CommentQueueProducer(queue_name="comment_queue")

    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=5,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=False
        )
        video = api.video(id=video_id)

        with open(output_path, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["author", "text"])

            index = 0
            async for comment in video.comments(count=1000):
                author = comment.author.username
                text = normalize_comment(comment.text)

                writer.writerow([author, text])

                try:
                    producer.send_comment_to_queue(
                        text=text,
                        author=f"{author}_{index}",
                        video_id=video_id,
                        is_final=False
                    )
                    index += 1
                except Exception as e:
                    print(f"❌ Lỗi gửi comment #{index}: {e}")

    # Gửi message cuối cùng báo hiệu hoàn tất
    try:
        producer.send_comment_to_queue(
            text="",
            author="",
            video_id=video_id,
            is_final=True
        )
        print("✅ Gửi message cuối cùng báo hiệu kết thúc.")
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

def normalize_comment(text):
    text = text.lower()
    text = clean_whitespace(text)
    text = remove_emoji(text)
    text = remove_special_characters(text)
    return text

def extract_video_id(tiktok_url):
    print(f"URL received: {tiktok_url}")
    match = re.search(r'/video/(\d+)', tiktok_url)
    if not match:
        match = re.search(r'/photo/(\d+)', tiktok_url)
    return match.group(1) if match else None
