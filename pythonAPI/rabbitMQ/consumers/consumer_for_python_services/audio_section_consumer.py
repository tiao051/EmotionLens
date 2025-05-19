def create_audio_callback(audio_model, label_encoder):
    def callback(ch, method, properties, body):
        import json
        message = json.loads(body)
        file_path = message["file_path"]
        video_id = message.get("video_id", "unknown")
        section_index = message.get("section_index", -1)

        print(f"🎧 Processing section {section_index} of video '{video_id}' from: {file_path}")

        emotion = audio_model.predict_emotion(file_path)
        label = label_encoder.inverse_transform([emotion])[0]

        print(f"🎤 Section {section_index} → Detected Emotion: {label}")

        ch.basic_ack(delivery_tag=method.delivery_tag)

    return callback
