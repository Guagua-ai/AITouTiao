import json
import requests

# Add this custom method to make the API request
def create_chat_completion(api_key, model, messages):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": model,
        "messages": messages
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.json()