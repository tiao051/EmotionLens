from TikTokApi import TikTokApi
import asyncio
import os
import csv
import re
import emoji

# Video ID và ms_token
video_id = 7474958652093369607
ms_token = "m3RZea0uuSNtoSje4jeilxcLfagz5tgbKBLtAIroQPnSMdnwTf6J3x_3v_4E2rnQ9C7AnzsrdcruF7Uuq4OGch6GZ27tYs8brzUMF5T3cC7U3fMK6FD3A9xpTyG19oyHeWjrrCV2wNHl0O6ldCvGVGfB"

async def get_comments():
    # Mở file CSV để ghi dữ liệu
    with open("comments.csv", mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        # Ghi dòng tiêu đề
        writer.writerow(["Comment", "Author"])

        # Khởi tạo API và tạo session
        async with TikTokApi() as api:
            await api.create_sessions(
                ms_tokens=[ms_token],
                num_sessions=1,
                sleep_after=5,
                browser=os.getenv("TIKTOK_BROWSER", "chromium"),
                headless=False  # Đặt thành False để nhìn thấy trình duyệt hoạt động
            )

            # Lấy video
            video = api.video(id=video_id)

            # Lấy bình luận
            async for comment in video.comments(count=1000):
                raw_text = comment.text
                comment_text = NormalizeComment(raw_text)
                author = comment.author.username
                # Ghi dữ liệu vào file CSV
                writer.writerow([author, comment_text])
                # In ra console (tùy chọn)
                #print(f"Comment: {comment_text} | Author: {author}")

def clean_whitespace(text):
    return ' '.join(text.strip().split())

def remove_emoji(text):
    return emoji.replace_emoji(text, replace='')

def remove_special_characters(text):
    # Giữ lại chữ cái (kể cả có dấu), số, và khoảng trắng
    return re.sub(r"[^\w\sÀ-ỹà-ỹ]", "", text)

def NormalizeComment(text):
    # Chuyển đổi sang chữ thường
    text = text.lower()
    
    # xoá khoảng trắng thừa
    text = clean_whitespace(text)
    
    # Xóa các ký tự emoji
    text = remove_emoji(text)
    
    # Xóa các ký tự đặc biệt
    text = remove_special_characters(text)
    
    return text

if __name__ == "__main__":
    asyncio.run(get_comments())
