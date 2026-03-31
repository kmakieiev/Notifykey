import os
import time
import json
import requests
from dotenv import load_dotenv
from snmp_scanner import get_keys_status
from db_manager import load_keys, save_keys  # <--- Добавили save_keys

# Подгружаем секреты
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

if not TOKEN or not ADMIN_ID:
    print("🚨 Ошибка: Не найден токен или ID админа в файле .env!")
    exit(1)

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# Главное меню вынесем в отдельную переменную, чтобы удобно было возвращать
MAIN_MENU = {
    "keyboard": [
        [{"text": "🔄 Статус ключей"}],
        [{"text": "⚙️ Настройки"}]
    ],
    "resize_keyboard": True,
    "is_persistent": True
}


def get_updates(offset=None):
    url = f"{BASE_URL}getUpdates"
    params = {"timeout": 3, "offset": offset}
    try:
        response = requests.get(url, params=params)
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка сети: {e}")
        return None


def send_message(chat_id, text, reply_markup=None):
    url = f"{BASE_URL}sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup)
    requests.post(url, json=payload)


def process_status_request(chat_id):
    send_message(chat_id, "Опрашиваю свитч... ⏳")
    status_dict = get_keys_status()
    keys_db = load_keys()

    if status_dict:
        reply_text = "Текущее состояние ключей:\n\n"
        for port, state in sorted(status_dict.items()):
            key_name = keys_db.get(str(port), {}).get("name", f"Ключ {port}")
            reply_text += f"{key_name} (Порт {port}): {state}\n"
    else:
        reply_text = "Ошибка связи со свитчом! ⚠️"

    send_message(chat_id, reply_text)


def main():
    print("Бот запущен и перешел в режим ожидания...")
    last_update_id = None
    previous_state = get_keys_status() or {}

    # --- FSM ПАМЯТЬ ---
    # Словарь, где мы будем хранить текущий шаг диалога для каждого юзера
    user_states = {}

    while True:
        updates = get_updates(last_update_id)

        if updates and updates.get("ok"):
            for item in updates["result"]:
                last_update_id = item["update_id"] + 1

                if "message" in item:
                    message = item["message"]
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")

                    if chat_id and text:
                        text = text.strip()

                        # --- 🛡️ ЩИТ БЕЗОПАСНОСТИ ---
                        if str(chat_id) != str(ADMIN_ID):
                            print(f"🚨 Попытка доступа от чужака: {chat_id}")
                            send_message(chat_id, "⛔️ Доступ запрещен. Я работаю только со своим создателем.")
                            continue  # Команда continue прерывает текущий шаг цикла. Бот забудет про это сообщение.
                        # ---------------------------

                        print(f"[{chat_id}]: {text}")

                        # --- ЛОГИКА ОТМЕНЫ ДЕЙСТВИЯ ---
                        if text == "❌ Отмена":
                            if chat_id in user_states:
                                del user_states[chat_id]  # Стираем память состояний
                            send_message(chat_id, "Действие отменено.", reply_markup=MAIN_MENU)
                            continue  # Переходим к следующему сообщению, игнорируя код ниже

                        # --- FSM: ПРОВЕРЯЕМ, НАХОДИТСЯ ЛИ ЮЗЕР В ДИАЛОГЕ ---
                        current_state = user_states.get(chat_id, {}).get("state")

                        if current_state == "WAITING_FOR_PORT":
                            valid_ports = ["2", "3", "4", "5", "6", "7"]
                            if text in valid_ports:
                                # Юзер ввел правильный порт. Запоминаем его и переводим на следующий шаг
                                user_states[chat_id] = {"state": "WAITING_FOR_NAME", "port": text}
                                send_message(
                                    chat_id,
                                    f"Выбран порт {text}. Введи новое имя для этого ключа:",
                                    reply_markup={"keyboard": [[{"text": "❌ Отмена"}]], "resize_keyboard": True}
                                )
                            else:
                                send_message(chat_id, "Пожалуйста, выбери номер порта от 2 до 7 (или нажми Отмена).")
                            continue  # Прерываем стандартную обработку

                        elif current_state == "WAITING_FOR_NAME":
                            # Юзер прислал новое имя!
                            port = user_states[chat_id]["port"]
                            keys_db = load_keys()

                            # Обновляем базу
                            if port not in keys_db:
                                keys_db[port] = {}
                            keys_db[port]["name"] = text
                            save_keys(keys_db)

                            # Сбрасываем состояние и возвращаем главное меню
                            del user_states[chat_id]
                            send_message(chat_id, f"✅ Супер! Ключ на порту {port} теперь называется «{text}».",
                                         reply_markup=MAIN_MENU)
                            continue

                        # --- СТАНДАРТНАЯ МАРШРУТИЗАЦИЯ (ЕСЛИ ЮЗЕР НЕ В ДИАЛОГЕ) ---
                        if text == "/start":
                            send_message(chat_id, "Привет! На связи твоя ключница.", reply_markup=MAIN_MENU)

                        elif text in ["/status", "🔄 Статус ключей"]:
                            process_status_request(chat_id)

                        elif text == "⚙️ Настройки":
                            # Запускаем диалог FSM
                            user_states[chat_id] = {"state": "WAITING_FOR_PORT"}

                            # Делаем удобную клавиатуру с номерами портов
                            ports_keyboard = {
                                "keyboard": [
                                    [{"text": "2"}, {"text": "3"}, {"text": "4"}],
                                    [{"text": "5"}, {"text": "6"}, {"text": "7"}],
                                    [{"text": "❌ Отмена"}]
                                ],
                                "resize_keyboard": True
                            }
                            send_message(chat_id, "Какой физический порт (2-7) ты хочешь переименовать?",
                                         reply_markup=ports_keyboard)

                        else:
                            send_message(chat_id, "Я такой команды не знаю. Воспользуйся меню 👇",
                                         reply_markup=MAIN_MENU)

        # --- БЛОК 2: ФОНОВЫЙ МОНИТОРИНГ (PUSH-АЛЕРТЫ) ---
        current_state = get_keys_status()
        if current_state:
            keys_db = load_keys()
            for port, current_status in current_state.items():
                old_status = previous_state.get(port)
                if old_status and current_status != old_status:
                    key_name = keys_db.get(str(port), {}).get("name", f"Ключ {port}")
                    alert_msg = f"🔔 Внимание! {key_name} (Порт {port}): {current_status}"
                    send_message(ADMIN_ID, alert_msg)
                    print(alert_msg)
            previous_state = current_state

        time.sleep(0.1)


if __name__ == "__main__":
    main()