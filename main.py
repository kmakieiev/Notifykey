import time
from config import ADMIN_ID, MAIN_MENU
from tg_api import get_updates, send_message
from snmp_scanner import get_keys_status
from db_manager import load_keys, save_keys


def process_status_request(chat_id):
    """
    Unified handler for requesting and sending the current status of all keys.
    """
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
    print("Bot started and waiting for updates...")
    last_update_id = None
    previous_state = get_keys_status() or {}

    # --- FSM MEMORY ---
    # Dictionary to store the current dialogue state for each user
    user_states = {}

    while True:
        # --- BLOCK 1: HANDLE INCOMING TELEGRAM UPDATES ---
        updates = get_updates(last_update_id)

        if updates and updates.get("ok"):
            for item in updates["result"]:
                last_update_id = item["update_id"] + 1

                if "message" in item:
                    message = item["message"]
                    chat_id = str(message.get("chat", {}).get("id"))
                    text = message.get("text", "")

                    if chat_id and text:
                        text = text.strip()

                        # --- SECURITY SHIELD ---
                        if chat_id != str(ADMIN_ID):
                            print(f"🚨 Unauthorized access attempt from: {chat_id}")
                            send_message(chat_id, "⛔️ Доступ запрещен. Я работаю только со своим создателем.")
                            continue

                        print(f"[{chat_id}]: {text}")

                        # --- CANCEL ACTION LOGIC ---
                        if text == "❌ Отмена":
                            if chat_id in user_states:
                                del user_states[chat_id]
                            send_message(chat_id, "Действие отменено.", reply_markup=MAIN_MENU)
                            continue

                        # --- FSM: CHECK IF USER IS IN A DIALOGUE STATE ---
                        current_state = user_states.get(chat_id, {}).get("state")

                        if current_state == "WAITING_FOR_PORT":
                            valid_ports = ["2", "3", "4", "5", "6", "7"]
                            if text in valid_ports:
                                user_states[chat_id] = {"state": "WAITING_FOR_NAME", "port": text}
                                send_message(
                                    chat_id,
                                    f"Выбран порт {text}. Введи новое имя для этого ключа:",
                                    reply_markup={"keyboard": [[{"text": "❌ Отмена"}]], "resize_keyboard": True}
                                )
                            else:
                                send_message(chat_id, "Пожалуйста, выбери номер порта от 2 до 7 (или нажми Отмена).")
                            continue

                        elif current_state == "WAITING_FOR_NAME":
                            port = user_states[chat_id]["port"]
                            keys_db = load_keys()

                            if port not in keys_db:
                                keys_db[port] = {}
                            keys_db[port]["name"] = text
                            save_keys(keys_db)

                            del user_states[chat_id]
                            send_message(chat_id, f"✅ Супер! Ключ на порту {port} теперь называется «{text}».",
                                         reply_markup=MAIN_MENU)
                            continue

                        # --- STANDARD ROUTING (IF USER IS NOT IN A DIALOGUE) ---
                        if text == "/start":
                            send_message(chat_id, "Привет! На связи твоя ключница.", reply_markup=MAIN_MENU)

                        elif text in ["/status", "🔄 Статус ключей"]:
                            process_status_request(chat_id)

                        elif text == "⚙️ Настройки":
                            user_states[chat_id] = {"state": "WAITING_FOR_PORT"}
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

        # --- BLOCK 2: BACKGROUND HARDWARE MONITORING (PUSH ALERTS) ---
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