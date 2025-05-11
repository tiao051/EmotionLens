import json

BASE_EMOTIONS = ['Angry', 'Disgust', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']

def callback_url(ch, method, properties, body):
    message = json.loads(body)

    print("== Received Full Message ==")
    print(json.dumps(message, indent=4))

    # 1. Lấy ChannelDes
    channel_desc = message.get("ChannelDes", "")

    # 2. Xác định domain
    domain = detect_domain(channel_desc)
    print(f"📌 Detected domain: {domain}")

    # 3. Cảm xúc mà model dự đoán
    predicted_emotion = "Sad"  # Ví dụ cảm xúc dự đoán từ mô hình

    # 4. Ánh xạ cảm xúc đã dự đoán theo domain
    mapped_emotion = map_emotion_to_domain(predicted_emotion, domain)
    print(f"🎭 Mapped emotion for this domain: {mapped_emotion}")

    # 5. xử lý file tại đây...

    ch.basic_ack(delivery_tag=method.delivery_tag)
    print(f"✅ File with ID {message.get('Id')} processed and acknowledged.")

def detect_domain(channel_description: str) -> str:
    if not channel_description:
        return "unknown"

    desc = channel_description.lower()

    if any(k in desc for k in ['youtuber', 'creator', 'content creator']):
        return 'youtuber'
    if any(k in desc for k in ['singer', 'musician', 'songwriter', 'music']):
        return 'singer'
    if any(k in desc for k in ['actor', 'actress', 'movie', 'drama', 'film']):
        return 'movie'
    if any(k in desc for k in ['gamer', 'gaming', 'gameplay', 'fps']):
        return 'gamer'
    if any(k in desc for k in ['vlog', 'lifestyle', 'travel', 'daily life']):
        return 'vlog'
    if any(k in desc for k in ['learn', 'education', 'science', 'coding', 'tech']):
        return 'education'
    if any(k in desc for k in ['beauty', 'makeup', 'fashion']):
        return 'beauty'
    if any(k in desc for k in ['funny', 'comedy', 'meme']):
        return 'comedy'

    return 'unknown'

def map_emotion_to_domain(emotion: str, domain: str) -> str:
    domain_mapping = {
        'singer': {
            'Sad': 'Touching',
            'Happy': 'Joyful',
            'Fear': 'Anxious',
            'Surprise': 'Amazed',
            'Angry': 'Frustrated',
            'Neutral': 'Calm'
        },
        'education': {
            'Sad': 'Disappointed',
            'Happy': 'Motivated',
            'Fear': 'Anxious',
            'Surprise': 'Curious',
            'Angry': 'Frustrated',
            'Neutral': 'Bored'
        },
        'gamer': {
            'Sad': 'Frustrated',
            'Happy': 'Excited',
            'Fear': 'Tense',
            'Surprise': 'Shocked',
            'Angry': 'Rage',
            'Neutral': 'Focused'
        },
        'movie': {
            'Sad': 'Heartbreaking',
            'Happy': 'Heartwarming',
            'Fear': 'Scary',
            'Surprise': 'Unexpected',
            'Angry': 'Raging',
            'Neutral': 'Suspense'
        },
        'vlog': {
            'Sad': 'Melancholic',
            'Happy': 'Cheerful',
            'Fear': 'Apprehensive',
            'Surprise': 'Unexpected',
            'Angry': 'Irritated',
            'Neutral': 'Chill'
        },
        'beauty': {
            'Sad': 'Sombre',
            'Happy': 'Radiant',
            'Fear': 'Nervous',
            'Surprise': 'Astonished',
            'Angry': 'Irritated',
            'Neutral': 'Natural'
        },
        'comedy': {
            'Sad': 'Silly',
            'Happy': 'Hilarious',
            'Fear': 'Clumsy',
            'Surprise': 'Witty',
            'Angry': 'Outrageous',
            'Neutral': 'Lighthearted'
        },
        'youtuber': {
            'Sad': 'Lonely',
            'Happy': 'Excited',
            'Fear': 'Concerned',
            'Surprise': 'Shocking',
            'Angry': 'Frustrated',
            'Neutral': 'Casual'
        },
        'unknown': {
            'Sad': 'Sad',
            'Happy': 'Happy',
            'Fear': 'Fear',
            'Surprise': 'Surprise',
            'Angry': 'Angry',
            'Neutral': 'Neutral'
        }
    }
    # Nếu emotion có trong domain, trả về emotion đã được ánh xạ
    return domain_mapping.get(domain, domain_mapping['unknown']).get(emotion, emotion)
