from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
import torch

# 1. Load model và tokenizer từ thư mục đã tải về
model = DistilBertForSequenceClassification.from_pretrained("./best_model")
tokenizer = DistilBertTokenizer.from_pretrained("./best_model")

# 2. Set chế độ đánh giá (không cần train)
model.eval()

# 3. Nhập văn bản cần phân loại
text = "I feel great today! Thank you for your help."

# 4. Tokenize văn bản
inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=128)

# 5. Dự đoán cảm xúc
with torch.no_grad():
    outputs = model(**inputs)
    predicted_class_id = torch.argmax(outputs.logits, dim=1).item()

# 6. Ánh xạ lại thành nhãn gốc (nếu bạn biết id2label)
id2label = model.config.id2label
predicted_label = id2label[str(predicted_class_id)]

print(f"Predicted label: {predicted_label}")
