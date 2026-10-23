import time
from config import ADMIN_ID, get_main_menu, get_alert_menu, get_language_menu
from tg_api import get_updates, send_message, delete_message
from snmp_scanner import get_keys_status
from db_manager import load_keys, save_keys, log_event, get_history, load_language, save_language
from localization import t, set_language, get_available_languages, get_language_name

# Memory for "Clean Chat" functionality
chat_memory = {}


def update_bot_message(chat_id, text, reply_markup=None):
    """
    Deletes the previous bot message and sends a new one.
    Returns the ID of the new message and saves it to memory.
    """
    if chat_id in chat_memory:
        delete_message(chat_id, chat_memory[chat_id])

    msg_id = send_message(chat_id, text, reply_markup)
    if msg_id:
        chat_memory[chat_id] = msg_id
    return msg_id


def process_status_request(chat_id):
    """Poll the switch with UI delay for loading effect."""
    update_bot_message(chat_id, t("querying_switch"), get_main_menu())
    time.sleep(3)  # Simulate busy activity for UI effect

    status_dict = get_keys_status()
    keys_db = load_keys()

    if status_dict:
        reply_text = t("current_key_status")
        for port, state in sorted(status_dict.items()):
            key_name = keys_db.get(str(port), {}).get("name", t("key_default_name", port=port))
            reply_text += f"{key_name} (Port {port}): {state}\n"
    else:
        reply_text = t("switch_error")

    update_bot_message(chat_id, reply_text, get_main_menu())


def main():
    # Load saved language preference FIRST
    saved_lang = load_language()
    set_language(saved_lang)

    print(t("bot_started"))

    last_update_id = None
    previous_state = get_keys_status() or {}
    last_snmp_poll = time.monotonic()
    snmp_poll_interval = 5.0

    user_states = {}

    while True:
        # --- BLOCK 1: PROCESS INCOMING UPDATES FROM TELEGRAM ---
        updates = get_updates(last_update_id)

        if updates and updates.get("ok"):
            for item in updates["result"]:
                last_update_id = item["update_id"] + 1

                if "message" in item:
                    message = item["message"]
                    chat_id = str(message.get("chat", {}).get("id"))
                    text = message.get("text", "").strip()
                    message_id = message.get("message_id")

                    # 1. Security check (silently drop unauthorized updates)
                    if chat_id != str(ADMIN_ID):
                        print(f"🚨 {t('unauthorized_attempt')} {chat_id}")
                        continue

                    # 2. Delete user message (Clean Chat)
                    if message_id:
                        delete_message(chat_id, message_id)

                    print(f"[{chat_id}]: {text}")

                    # 3. PRIORITY INTERRUPT (ALERTS)
                    current_state = user_states.get(chat_id, {}).get("state")

                    if current_state == "WAITING_FOR_ALERT_ACK":
                        if text == t("btn_ok"):
                            del user_states[chat_id]
                            update_bot_message(chat_id, t("returning_to_menu"), get_main_menu())
                        elif text == t("btn_history"):
                            hist_text = get_history()
                            update_bot_message(chat_id, t("recent_events") + hist_text, get_main_menu())
                            del user_states[chat_id]
                        else:
                            # If user clicks something else, keep them locked until they confirm the alert
                            update_bot_message(chat_id, t("confirm_alert"), get_alert_menu())
                        continue  # Completely block execution of remaining commands

                    # 4. Cancel current action
                    if text == t("btn_cancel"):
                        if chat_id in user_states:
                            del user_states[chat_id]
                        update_bot_message(chat_id, t("action_cancelled"), get_main_menu())
                        continue

                    # 5. Language Selection
                    if text == t("btn_language"):
                        user_states[chat_id] = {"state": "WAITING_FOR_LANGUAGE"}
                        update_bot_message(chat_id, t("select_language"), get_language_menu())
                        continue

                    if current_state == "WAITING_FOR_LANGUAGE":
                        available_langs = get_available_languages()
                        lang_names = {get_language_name(lang): lang for lang in available_langs}

                        if text in lang_names:
                            lang_code = lang_names[text]
                            set_language(lang_code)
                            save_language(lang_code)
                            del user_states[chat_id]
                            update_bot_message(
                                chat_id,
                                f"✅ Language changed to {get_language_name(lang_code)}",
                                get_main_menu()
                            )
                        else:
                            update_bot_message(chat_id, t("select_language"), get_language_menu())
                        continue

                    # 6. State machine (Settings)
                    if current_state == "WAITING_FOR_PORT":
                        valid_ports = ["2", "3", "4", "5", "6", "7"]
                        if text in valid_ports:
                            user_states[chat_id] = {"state": "WAITING_FOR_NAME", "port": text}
                            update_bot_message(
                                chat_id,
                                t("port_selected", port=text),
                                reply_markup={"keyboard": [[{"text": t("btn_cancel")}]], "resize_keyboard": True}
                            )
                        else:
                            update_bot_message(chat_id, t("select_port"), get_main_menu())
                        continue

                    elif current_state == "WAITING_FOR_NAME":
                        port = user_states[chat_id]["port"]
                        keys_db = load_keys()
                        if port not in keys_db: keys_db[port] = {}
                        keys_db[port]["name"] = text
                        save_keys(keys_db)
                        del user_states[chat_id]
                        update_bot_message(chat_id, t("key_renamed", port=port, name=text), get_main_menu())
                        continue

                    # 7. Main routing
                    if text == "/start":
                        update_bot_message(chat_id, t("hello"), get_main_menu())

                    elif text in ["/status", t("btn_key_status")]:
                        process_status_request(chat_id)

                    elif text == t("btn_settings"):
                        user_states[chat_id] = {"state": "WAITING_FOR_PORT"}
                        ports_keyboard = {
                            "keyboard": [
                                [{"text": "2"}, {"text": "3"}, {"text": "4"}],
                                [{"text": "5"}, {"text": "6"}, {"text": "7"}],
                                [{"text": t("btn_cancel")}]
                            ],
                            "resize_keyboard": True
                        }
                        update_bot_message(chat_id, t("which_port"), ports_keyboard)

                    else:
                        update_bot_message(chat_id, t("command_not_recognized"), get_main_menu())

        # --- BLOCK 2: BACKGROUND HARDWARE MONITORING ---
        now = time.monotonic()
        if now - last_snmp_poll >= snmp_poll_interval:
            last_snmp_poll = now
            current_hw_state = get_keys_status()
            if current_hw_state:
                keys_db = load_keys()
                for port, status in current_hw_state.items():
                    old_status = previous_state.get(port)
                    if old_status and status != old_status:
                        key_name = keys_db.get(str(port), {}).get("name", t("key_default_name", port=port))

                        # 1. Write event to history log
                        log_event(port, key_name, status)

                        # 2. FORCE interrupt the dialog (set alert state)
                        user_states[ADMIN_ID] = {"state": "WAITING_FOR_ALERT_ACK"}

                        # 3. Show priority notification
                        alert_msg = t("alert_message", key_name=key_name, port=port, status=status)
                        update_bot_message(ADMIN_ID, alert_msg, get_alert_menu())
                        print(f"{t('alert_pushed')} {alert_msg}")

                previous_state = current_hw_state

        time.sleep(0.5)


if __name__ == "__main__":
    main()