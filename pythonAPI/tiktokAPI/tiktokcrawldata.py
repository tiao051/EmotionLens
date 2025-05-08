from TikTokApi import TikTokApi
import asyncio
import os
import csv
import re
import emoji

async def get_comments(video_id: str, ms_token: str, output_path: str = "comments.csv"):
    async with TikTokApi() as api:
        await api.create_sessions(
            ms_tokens=[ms_token],
            num_sessions=1,
            sleep_after=5,
            browser=os.getenv("TIKTOK_BROWSER", "chromium"),
            headless=True
        )
        video = api.video(id=video_id)
        async for comment in video.comments(count=1000):
            author = comment.author.username
            text = normalizeComment(comment.text)
            with open(output_path, "a", encoding="utf-8", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([author, text])

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
