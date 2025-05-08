import requests
import json
from config import API_ENDPOINTS

def send_result_to_api(endpoint_key, file_id, emotion_result):
    result_message = {
        "Id": file_id,
        "Emotion": emotion_result
    }
    url = API_ENDPOINTS[endpoint_key]
    headers = {"Content-Type": "application/json"}

    print(f"Data sent to C#: {result_message}")
    try:
        response = requests.post(url, json=result_message, headers=headers, verify=False)
        print(f"Response from C#: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to C#: {e}")
