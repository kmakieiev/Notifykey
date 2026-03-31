import json
import requests
from config import BASE_URL


def get_updates(offset=None):
    """Fetches updates from the Telegram API using Long Polling."""
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
    Sends a text message to a specific chat.
    RETURNS the message_id of the sent message (crucial for editing/deleting later).
    """
    url = f"{BASE_URL}sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    response = requests.post(url, json=payload)

    # Пытаемся вытащить message_id из ответа Telegram
    if response.status_code == 200:
        data = response.json()
        if data.get("ok"):
            return data["result"]["message_id"]
    return None


def delete_message(chat_id, message_id):
    """Deletes a specific message from the chat."""
    url = f"{BASE_URL}deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    requests.post(url, json=payload)


def edit_message(chat_id, message_id, text, reply_markup=None):
    """Edits the text of an already sent bot message."""
    url = f"{BASE_URL}editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, json=payload)