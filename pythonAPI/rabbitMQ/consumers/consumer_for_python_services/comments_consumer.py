import json
import threading
import asyncio
from collections import defaultdict
from config import API_ENDPOINTS
from rabbitMQ.services.api_client import send_to_api_async
import torch

def map_emotion_label(class_id):
    mapping = {
        0: "angry",
        1: "sad",
        2: "neutral",
        3: "happy",
        4: "surprise"
    }
    if isinstance(class_id, str) and class_id.isdigit():
        class_id = int(class_id)
    return mapping.get(class_id, str(class_id))

def create_comment_callback(model, tokenizer, id2label):
    # Dùng closure để giữ model/tokenizer/id2label
    comment_buffer = defaultdict(list)
    lock = threading.Lock()
    BATCH_SIZE = 16

    async def process_comment_batch_async(comments):
        try:
            texts = [c.get("Text", "") for c in comments]
            authors = [c.get("author") for c in comments]
            video_id = comments[0].get("video_id", "unknown")

            inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=128)
            with torch.no_grad():
                outputs = model(**inputs)
                predicted_ids = torch.argmax(outputs.logits, dim=1).tolist()

            result_message = {
                "VideoId": video_id,
                "Results": []
            }

            results = []
            for idx, class_id in enumerate(predicted_ids):
                author = authors[idx]
                label = map_emotion_label(class_id)
                if not author or not label:
                    print(f"⚠️ Bỏ qua comment không hợp lệ: author={author}, emotion={label}")
                    continue
                print(f"[Batch] {author} → {label}")
                results.append({
                    "Author": author,    
                    "Result": label
                })

            if results:
                result_message = {
                    "VideoId": video_id, 
                    "Results": results
                }
                print(f"Sending batch result to C#:")
                await send_to_api_async(result_message, API_ENDPOINTS["multi_text"])
            else:
                print("⚠️ Không có comment hợp lệ nào để gửi batch.")

        except Exception as e:
            print(f"❌ Error in batch processing comments: {e}")



    def process_comment_video(video_id):
        with lock:
            comments = comment_buffer.pop(video_id, [])
        if not comments:
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(process_comment_batch_async(comments))
        loop.close()

    def process_comment_message(body):
        try:
            msg = json.loads(body)
            vid = msg.get('video_id', 'default')
            is_final = msg.get('is_final', False)

            with lock:
                comment_buffer[vid].append(msg)
                if len(comment_buffer[vid]) >= BATCH_SIZE or (is_final and comment_buffer[vid]):
                    threading.Thread(target=process_comment_video, args=(vid,), daemon=True).start()
        except Exception as e:
            print(f"❌ Error processing comment message: {e}")

    async def callback_comment(ch, method, properties, body):
        process_comment_message(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    return callback_comment
