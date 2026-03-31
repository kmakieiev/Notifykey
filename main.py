import time
from config import ADMIN_ID, MAIN_MENU, ALERT_MENU
from tg_api import get_updates, send_message, delete_message
from snmp_scanner import get_keys_status
from db_manager import load_keys, save_keys, log_event, get_history

# Память для "Чистого чата"
chat_memory = {}


def update_bot_message(chat_id, text, reply_markup=None):
    """
    Удаляет предыдущее сообщение бота и отправляет новое.
    Возвращает ID нового сообщения и сохраняет его в память.
    """
    if chat_id in chat_memory:
        delete_message(chat_id, chat_memory[chat_id])

    msg_id = send_message(chat_id, text, reply_markup)
    if msg_id:
        chat_memory[chat_id] = msg_id
    return msg_id


def process_status_request(chat_id):
    """Опрос свитча с UI-задержкой для эффекта загрузки."""
    update_bot_message(chat_id, "Опрашиваю свитч... ⏳", MAIN_MENU)
    time.sleep(3)  # Имитация бурной деятельности для UI

    status_dict = get_keys_status()
    keys_db = load_keys()

    if status_dict:
        reply_text = "Текущее состояние ключей:\n\n"
        for port, state in sorted(status_dict.items()):
            key_name = keys_db.get(str(port), {}).get("name", f"Ключ {port}")
            reply_text += f"{key_name} (Порт {port}): {state}\n"
    else:
        reply_text = "Ошибка связи со свитчом! ⚠️"

    update_bot_message(chat_id, reply_text, MAIN_MENU)


def main():
    print("Bot started with Clean Chat and Event-Driven UI...")
    last_update_id = None
    previous_state = get_keys_status() or {}

    user_states = {}

    while True:
        # --- БЛОК 1: ОБРАБОТКА ВХОДЯЩИХ ОТ ТЕЛЕГРАМ ---
        updates = get_updates(last_update_id)

        if updates and updates.get("ok"):
            for item in updates["result"]:
                last_update_id = item["update_id"] + 1

                if "message" in item:
                    message = item["message"]
                    chat_id = str(message.get("chat", {}).get("id"))
                    text = message.get("text", "").strip()
                    message_id = message.get("message_id")

                    # 1. Секьюрити контроль
                    if chat_id != str(ADMIN_ID):
                        print(f"🚨 Unauthorized attempt: {chat_id}")
                        send_message(chat_id, "⛔️ Доступ запрещен.")
                        continue

                    # 2. Удаляем сообщение юзера (Clean Chat)
                    if message_id:
                        delete_message(chat_id, message_id)

                    print(f"[{chat_id}]: {text}")

                    # 3. ПРИОРИТЕТНОЕ ПРЕРЫВАНИЕ (АЛЕРТЫ)
                    current_state = user_states.get(chat_id, {}).get("state")

                    if current_state == "WAITING_FOR_ALERT_ACK":
                        if text == "✅ OK":
                            del user_states[chat_id]
                            update_bot_message(chat_id, "Возвращаемся в меню.", MAIN_MENU)
                        elif text == "📜 История":
                            hist_text = get_history()
                            update_bot_message(chat_id, f"Последние события:\n\n{hist_text}", MAIN_MENU)
                            del user_states[chat_id]
                        else:
                            # Если юзер жмет что-то другое, не отпускаем его, пока не подтвердит алерт
                            update_bot_message(chat_id, "⚠️ Подтверди прочтение алерта!", ALERT_MENU)
                        continue  # Полностью блокируем выполнение остальных команд

                    # 4. Отмена текущего действия
                    if text == "❌ Отмена":
                        if chat_id in user_states:
                            del user_states[chat_id]
                        update_bot_message(chat_id, "Действие отменено.", MAIN_MENU)
                        continue

                    # 5. Машина состояний (Настройки)
                    if current_state == "WAITING_FOR_PORT":
                        valid_ports = ["2", "3", "4", "5", "6", "7"]
                        if text in valid_ports:
                            user_states[chat_id] = {"state": "WAITING_FOR_NAME", "port": text}
                            update_bot_message(
                                chat_id,
                                f"Выбран порт {text}. Введи новое имя:",
                                reply_markup={"keyboard": [[{"text": "❌ Отмена"}]], "resize_keyboard": True}
                            )
                        else:
                            update_bot_message(chat_id, "Выбери порт 2-7 или жми Отмена.")
                        continue

                    elif current_state == "WAITING_FOR_NAME":
                        port = user_states[chat_id]["port"]
                        keys_db = load_keys()
                        if port not in keys_db: keys_db[port] = {}
                        keys_db[port]["name"] = text
                        save_keys(keys_db)
                        del user_states[chat_id]
                        update_bot_message(chat_id, f"✅ Ключ на порту {port} теперь: «{text}»", MAIN_MENU)
                        continue

                    # 6. Основная маршрутизация
                    if text == "/start":
                        update_bot_message(chat_id, "Привет! Я твоя умная ключница.", MAIN_MENU)

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
                        update_bot_message(chat_id, "Какой порт переименовать?", ports_keyboard)

                    else:
                        update_bot_message(chat_id, "Команда не распознана. Используй меню 👇", MAIN_MENU)

        # --- БЛОК 2: ФОНОВЫЙ МОНИТОРИНГ ЖЕЛЕЗА ---
        current_hw_state = get_keys_status()
        if current_hw_state:
            keys_db = load_keys()
            for port, status in current_hw_state.items():
                old_status = previous_state.get(port)
                if old_status and status != old_status:
                    key_name = keys_db.get(str(port), {}).get("name", f"Ключ {port}")

                    # 1. Пишем в лог-файл историю
                    log_event(port, key_name, status)

                    # 2. ПРИНУДИТЕЛЬНО прерываем диалог (ставим состояние алерта)
                    user_states[ADMIN_ID] = {"state": "WAITING_FOR_ALERT_ACK"}

                    # 3. Выводим приоритетное уведомление
                    alert_msg = f"⚠️ ВНИМАНИЕ! ИЗМЕНЕНИЕ!\n\n{key_name} (Порт {port}): {status}"
                    update_bot_message(ADMIN_ID, alert_msg, ALERT_MENU)
                    print(f"Alert pushed: {alert_msg}")

            previous_state = current_hw_state

        time.sleep(0.1)


if __name__ == "__main__":
    main()