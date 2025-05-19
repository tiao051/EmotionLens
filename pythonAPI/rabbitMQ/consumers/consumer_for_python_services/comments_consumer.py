import json
import threading
import asyncio
from collections import defaultdict
from pathlib import Path
import torch
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification

# Global biến model/tokenizer/id2label
model = None
tokenizer = None
id2label = None

def load_text_model():
    global model, tokenizer, id2label
    MODEL_DIR = Path(r"D:\Deep_Learning\main\pythonAPI\emotion_model\text_model\best_model")
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
    tokenizer = DistilBertTokenizer.from_pretrained(MODEL_DIR)
    model.eval()
    id2label = model.config.id2label
    print(f"Text model loaded successfully from {MODEL_DIR}.")

def map_emotion_label(class_id):
    mapping = {
        0: "Very negative",
        1: "Negative",
        2: "Neutral",
        3: "Positive",
        4: "Very positive"
    }
    if isinstance(class_id, str) and class_id.isdigit():
        class_id = int(class_id)
    return mapping.get(class_id, str(class_id))

# Buffer và lock để gom batch
comment_buffer = defaultdict(list)
lock = threading.Lock()
BATCH_SIZE = 16

async def process_comment_batch_async(comments):
    try:
        texts   = [c.get("Text",  "") for c in comments]
        authors = [c.get("author") for c in comments]

        # Tokenize và predict
        inputs = tokenizer(texts, return_tensors="pt", truncation=True, padding=True, max_length=128)
        with torch.no_grad():
            outputs       = model(**inputs)
            predicted_ids = torch.argmax(outputs.logits, dim=1).tolist()

        # In kết quả
        for idx, class_id in enumerate(predicted_ids):
            label = map_emotion_label(class_id)
            print(f"[Batch] {authors[idx]} → {label}")

    except Exception as e:
        print(f"❌ Error in batch processing comments: {e}")

def process_comment_video(video_id):
    with lock:
        comments = comment_buffer.pop(video_id, [])
    if not comments:
        return

    # Tạo và chạy event loop riêng cho batch
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(process_comment_batch_async(comments))
    loop.close()

def process_comment_message(body):
    try:
        msg = json.loads(body)
        vid = msg.get('video_id', 'default')
        is_final = msg.get('is_final', False)

        # Thêm vào buffer
        with lock:
            comment_buffer[vid].append(msg)
            # Khi đủ batch hoặc cuối thì khởi chạy
            if len(comment_buffer[vid]) >= BATCH_SIZE or (is_final and comment_buffer[vid]):
                threading.Thread(target=process_comment_video, args=(vid,), daemon=True).start()
    except Exception as e:
        print(f"❌ Error processing comment message: {e}")

async def callback_comment(ch, method, properties, body):
    process_comment_message(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
