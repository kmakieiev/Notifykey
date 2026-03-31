import json
import requests
from config import BASE_URL


def get_updates(offset=None):
    """
    Fetches updates from the Telegram API using Long Polling.
    Returns the JSON response or None if a network error occurs.
    """
    url = f"{BASE_URL}getUpdates"
    params = {"timeout": 3, "offset": offset}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None


def send_message(chat_id, text, reply_markup=None):
    """
    Sends a text message to a specific Telegram chat.
    Optionally attaches a custom keyboard (reply_markup).
    """
    url = f"{BASE_URL}sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, json=payload)