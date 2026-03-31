import requests
import time
import os
from dotenv import load_dotenv
from snmp_scanner import get_keys_status

# Подгружаем переменные из файла .env в систему
load_dotenv()

# Достаем наши секреты безопасно
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN or not ADMIN_ID:
    print("🚨 Ошибка: Не найден токен или ID админа в файле .env!")
    exit(1) # Жестко останавливаем скрипт, если секретов нет

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# ... дальше идет твоя функция get_updates и весь остальной код без изменений ...

def get_updates(offset=None):
    url = f"{BASE_URL}getUpdates"
    params = {"timeout": 3, "offset": offset}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        return None


def send_message(chat_id, text):
    url = f"{BASE_URL}sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    requests.post(url, json=payload)


def main():
    print("Бот запущен и перешел в режим ожидания (Long Polling)...")
    last_update_id = None

    print("Сканирую начальное состояние ключей...")
    previous_state = get_keys_status()

    # На случай, если при старте свитч недоступен, делаем страховку
    if previous_state is None:
        previous_state = {}

    # Основной цикл
    while True:
        updates = get_updates(last_update_id)

        if updates and updates.get("ok"):
            for item in updates["result"]:
                last_update_id = item["update_id"] + 1

                message = item.get("message", {})
                chat_id = message.get("chat", {}).get("id")
                text = message.get("text", "")

                if chat_id and text:
                    text = text.strip()  # Защита от случайных пробелов
                    print(f"[{chat_id}]: {text}")

                    # --- БЛОК МАРШРУТИЗАЦИИ ---
                    if text == "/start":
                        send_message(chat_id, "Привет! На связи твоя ключница.\nЖми /status чтобы проверить ключи.")

                    elif text == "/status":
                        # Отправляем заглушку, чтобы юзер знал, что процесс пошел
                        send_message(chat_id, "Опрашиваю свитч... ⏳")

                        # Дергаем SNMP сканер
                        status_dict = get_keys_status()

                        # Формируем красивый текст ответа
                        if status_dict:
                            reply_text = "Текущее состояние ключей:\n\n"
                            for port, state in sorted(status_dict.items()):
                                reply_text += f"Ключ {port}: {state}\n"
                        else:
                            reply_text = "Ошибка связи со свитчом! ⚠️"

                        # Отправляем финальный результат
                        send_message(chat_id, reply_text)

                    else:
                        send_message(chat_id, "Я такой команды не знаю. Попробуй /status")

        time.sleep(0.1)

        # 1. Делаем свежий срез данных
        current_state = get_keys_status()

        # 2. Если данные пришли, начинаем детектив
        if current_state:
            for port, current_status in current_state.items():
                # Достаем старый статус этого же порта
                old_status = previous_state.get(port)

                # Если статусы не совпадают — бинго, что-то произошло!
                if current_status != old_status:
                    # Пушим уведомление админу!
                    alert_msg = f"🔔 Внимание! Изменение на порту {port}: {current_status}"
                    send_message(ADMIN_ID, alert_msg)
                    print(alert_msg)  # Дублируем в консоль для дебага

            # 3. Самое важное: обновляем память!
            # Текущее состояние становится прошлым для следующего круга
            previous_state = current_state


if __name__ == "__main__":
    main()