import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from sklearn.model_selection import train_test_split
import random

def get_label_maps(df):
    unique_labels = sorted(df['label'].unique())
    label2id = {label: i for i, label in enumerate(unique_labels)}
    id2label = {i: label for label, i in label2id.items()}
    return label2id, id2label

def synonym_augment(text):
    words = text.split()
    if len(words) < 2:
        return text
    i = random.randint(0, len(words)-2)
    words[i], words[i+1] = words[i+1], words[i]
    return " ".join(words)

def load_and_prepare_data(csv_path, model_name, max_len=64):
    df = pd.read_csv(csv_path)
    df = df[['text', 'sentiment']].dropna().rename(columns={'sentiment': 'label'})
    label2id, id2label = get_label_maps(df)
    df['label'] = df['label'].map(label2id)

    train_df, test_df = train_test_split(df, test_size=0.2, stratify=df['label'], random_state=42)

    # Augment train data
    augmented_texts = train_df['text'].apply(synonym_augment)
    augmented_df = pd.DataFrame({'text': augmented_texts, 'label': train_df['label']})
    train_df = pd.concat([train_df, augmented_df]).reset_index(drop=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    def tokenize(example):
        return tokenizer(example['text'], padding='max_length', truncation=True, max_length=max_len)

    train_dataset = Dataset.from_pandas(train_df).map(tokenize, batched=True)
    test_dataset = Dataset.from_pandas(test_df).map(tokenize, batched=True)

    model = AutoModelForSequenceClassification.from_pretrained(
        model_name,
        num_labels=len(label2id),
        id2label=id2label,
        label2id=label2id
    )

    return model, tokenizer, train_dataset, test_dataset, label2id, id2label
