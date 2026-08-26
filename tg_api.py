import json
import requests
from config import BASE_URL
from localization import t

REQUEST_TIMEOUT = 5
LONG_POLL_TIMEOUT = 35


def get_updates(offset=None):
    """Fetches updates from the Telegram API using Long Polling."""
    url = f"{BASE_URL}getUpdates"
    params = {"timeout": 30, "offset": offset}
    try:
        response = requests.get(url, params=params, timeout=LONG_POLL_TIMEOUT)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"{t('network_error')} {e}")
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

    try:
        response = requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)

        # Try to extract message_id from Telegram response
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                return data["result"]["message_id"]
    except requests.exceptions.RequestException as e:
        print(f"{t('network_error')} {e}")
    return None


def delete_message(chat_id, message_id):
    """Deletes a specific message from the chat."""
    url = f"{BASE_URL}deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        print(f"{t('network_error')} {e}")


def edit_message(chat_id, message_id, text, reply_markup=None):
    """Edits the text of an already sent bot message."""
    url = f"{BASE_URL}editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    try:
        requests.post(url, json=payload, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.RequestException as e:
        print(f"{t('network_error')} {e}")
