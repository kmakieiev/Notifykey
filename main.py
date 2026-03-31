import os
import time
import json
import requests
from dotenv import load_dotenv
from snmp_scanner import get_keys_status

# Подгружаем секреты
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN or not ADMIN_ID:
    print("🚨 Ошибка: Не найден токен или ID админа в файле .env!")
    exit(1)

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"


def get_updates(offset=None):
    """Получает обновления от Telegram."""
    url = f"{BASE_URL}getUpdates"
    params = {"timeout": 3, "offset": offset}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        return None


def send_message(chat_id, text, reply_markup=None):
    """Отправляет текстовое сообщение (с опциональной Reply-клавиатурой)."""
    url = f"{BASE_URL}sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)

    requests.post(url, json=payload)


def process_status_request(chat_id):
    """Единый обработчик для вывода статуса ключей (DRY)."""
    send_message(chat_id, "Опрашиваю свитч... ⏳")
    status_dict = get_keys_status()

    if status_dict:
        reply_text = "Текущее состояние ключей:\n\n"
        for port, state in sorted(status_dict.items()):
            reply_text += f"Ключ {port}: {state}\n"
    else:
        reply_text = "Ошибка связи со свитчом! ⚠️"

    send_message(chat_id, reply_text)


def main():
    print("Бот запущен и перешел в режим ожидания...")
    last_update_id = None

    # Инициализация памяти для Push-уведомлений
    print("Сканирую начальное состояние ключей...")
    previous_state = get_keys_status()
    if previous_state is None:
        previous_state = {}

    while True:
        # --- БЛОК 1: ОБРАБОТКА ВХОДЯЩИХ ОТ TELEGRAM ---
        updates = get_updates(last_update_id)

        if updates and updates.get("ok"):
            for item in updates["result"]:
                last_update_id = item["update_id"] + 1

                # Обрабатываем только текстовые сообщения
                if "message" in item:
                    message = item["message"]
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")

                    if chat_id and text:
                        text = text.strip()
                        print(f"[{chat_id}]: {text}")

                        if text == "/start":
                            # Выдаем постоянное главное меню
                            reply_keyboard = {
                                "keyboard": [
                                    [{"text": "🔄 Статус ключей"}]
                                ],
                                "resize_keyboard": True,
                                "is_persistent": True
                            }
                            send_message(
                                chat_id,
                                "Привет! На связи твоя ключница.\nГлавное меню активировано 👇",
                                reply_markup=reply_keyboard
                            )

                        # Реагируем и на команду, и на кнопку из меню
                        elif text in ["/status", "🔄 Статус ключей"]:
                            process_status_request(chat_id)

                        else:
                            send_message(chat_id, "Я такой команды не знаю. Воспользуйся кнопкой меню внизу экрана.")

        # --- БЛОК 2: ФОНОВЫЙ МОНИТОРИНГ ЖЕЛЕЗА (PUSH-АЛЕРТЫ) ---
        current_state = get_keys_status()

        if current_state:
            for port, current_status in current_state.items():
                old_status = previous_state.get(port)

                # Если статус изменился - пушим алерт админу
                if old_status and current_status != old_status:
                    alert_msg = f"🔔 Внимание! Изменение на порту {port}: {current_status}"
                    send_message(ADMIN_ID, alert_msg)
                    print(alert_msg)

            # Обновляем память для следующего цикла
            previous_state = current_state

        time.sleep(0.1)


if __name__ == "__main__":
    main()