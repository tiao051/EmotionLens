import json
import cv2 # type: ignore
import json
import threading
import numpy as np
from collections import defaultdict
from emotion_model.efficientNet_model.build import build_finetune_efficientnet

# Load EfficientNet model once
efficientnet_model = build_finetune_efficientnet(input_shape=(48, 48, 3), num_classes=7)

EMOTION_LABELS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

frame_buffer = defaultdict(list)
lock = threading.Lock()
BATCH_SIZE = 5

def predict_batch(images):
    # images: list of np.ndarray (grayscale)
    # Convert to shape (batch, 48, 48, 3) and normalize
    batch = []
    for img in images:
        if img is None:
            continue
        # Convert grayscale to 3 channels
        if len(img.shape) == 2:
            img = np.stack([img]*3, axis=-1)
        img = img.astype(np.float32) / 255.0
        img = cv2.resize(img, (48, 48))
        batch.append(img)
    if not batch:
        return []
    batch = np.stack(batch, axis=0)
    preds = efficientnet_model.predict(batch)
    pred_labels = [EMOTION_LABELS[np.argmax(p)] for p in preds]
    return pred_labels

def process_video(video_id):
    with lock:
        frames = frame_buffer.pop(video_id, [])
    if not frames:
        return json.dumps({
            "video_id": video_id,
            "message": "No frames found",
            "results": []
        })

    print(f"🧠 Processing video {video_id} with {len(frames)} frames")
    images = [cv2.imread(fp, cv2.IMREAD_GRAYSCALE) for fp in frames]
    results = predict_batch(images)

    response = {
        "video_id": video_id,
        "frame_count": len(frames),
        "results": []
    }

    for fp, res in zip(frames, results):
        print(f"✅ Frame: {fp} | Emotion: {res}")
        response["results"].append({
            "frame": fp,
            "emotion": res
        })

    return json.dumps(response, ensure_ascii=False, indent=2)

def process_frame_message(body):
    try:
        message = json.loads(body)
        video_id = message.get('video_id')
        file_path = message.get('FilePath')
        is_final = message.get('is_final', False)
        print(f"[x] Received frame: {message['Id']} at {message['FilePath']}")
        # Đưa frame vào buffer trước, chỉ gọi process_video khi đủ batch hoặc là frame cuối
        with lock:
            frame_buffer[video_id].append(file_path)
            if len(frame_buffer[video_id]) >= BATCH_SIZE or (is_final and len(frame_buffer[video_id]) > 0):
                threading.Thread(target=process_video, args=(video_id,)).start()
    except Exception as e:
        print(f"❌ Error processing frame message: {e}")

async def callback_frame(ch, method, properties, body):
    process_frame_message(body)
    ch.basic_ack(delivery_tag=method.delivery_tag)
