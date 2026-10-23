"""
Multi-language localization module for NotifyKey bot.
Supports: English, German, Russian, Ukrainian
"""

# Complete translation dictionary
TRANSLATIONS = {
    "en": {
        # UI Messages
        "querying_switch": "Querying switch... ⏳",
        "current_key_status": "Current key status:\n\n",
        "switch_error": "Switch communication error! ⚠️",
        "access_denied": "⛔️ Access denied.",
        "returning_to_menu": "Returning to menu.",
        "recent_events": "Recent events:\n\n",
        "confirm_alert": "⚠️ Please confirm you've read the alert!",
        "action_cancelled": "Action cancelled.",
        "port_selected": "Port {port} selected. Enter new name:",
        "select_port": "Select port 2-7 or click Cancel.",
        "key_renamed": "✅ Key on port {port} is now: «{name}»",
        "hello": "Hello! I'm your smart key keeper.",
        "which_port": "Which port to rename?",
        "command_not_recognized": "Command not recognized. Use the menu below 👇",
        "alert_message": "⚠️ ALERT! STATE CHANGE!\n\n{key_name} (Port {port}): {status}",
        "unauthorized_attempt": "Unauthorized attempt:",

        # Menu buttons
        "btn_key_status": "🔄 Key Status",
        "btn_settings": "⚙️ Settings",
        "btn_ok": "✅ OK",
        "btn_history": "📜 History",
        "btn_cancel": "❌ Cancel",
        "btn_language": "🌐 Language",

        # Database messages
        "history_empty": "History is empty 📭",
        "key_default_name": "Key {port}",
        "database_not_found": "Database not found. Creating an initial keys_db.json...",
        "json_error": "🚨 JSON Read Error! File is corrupted. Returning default settings.",
        "error_querying": "Error querying switch:",
        "key_inserted": "Inserted 🟢",
        "key_missing": "Missing 🔴",
        "network_error": "Network error:",
        "bot_started": "Bot started with Clean Chat and Event-Driven UI...",
        "alert_pushed": "Alert pushed:",

        # Language names
        "lang_english": "English",
        "lang_german": "Deutsch",
        "lang_russian": "Русский",
        "lang_ukrainian": "Українська",

        # Language selection
        "select_language": "Please select your language:",
    },
    "de": {
        # UI Messages
        "querying_switch": "Schalter wird abgefragt... ⏳",
        "current_key_status": "Aktueller Schlüsselstatus:\n\n",
        "switch_error": "Schalter-Kommunikationsfehler! ⚠️",
        "access_denied": "⛔️ Zugriff verweigert.",
        "returning_to_menu": "Zurück zum Menü.",
        "recent_events": "Letzte Ereignisse:\n\n",
        "confirm_alert": "⚠️ Bitte bestätigen Sie, dass Sie die Benachrichtigung gelesen haben!",
        "action_cancelled": "Aktion abgebrochen.",
        "port_selected": "Port {port} ausgewählt. Geben Sie einen neuen Namen ein:",
        "select_port": "Wählen Sie Port 2-7 oder klicken Sie auf Abbrechen.",
        "key_renamed": "✅ Schlüssel an Port {port} heißt jetzt: «{name}»",
        "hello": "Hallo! Ich bin dein intelligenter Schlüsselverwalter.",
        "which_port": "Welchen Port möchten Sie umbenennen?",
        "command_not_recognized": "Befehl nicht erkannt. Verwenden Sie das Menü unten 👇",
        "alert_message": "⚠️ WARNUNG! STATUSÄNDERUNG!\n\n{key_name} (Port {port}): {status}",
        "unauthorized_attempt": "Nicht autorisierter Versuch:",

        # Menu buttons
        "btn_key_status": "🔄 Schlüsselstatus",
        "btn_settings": "⚙️ Einstellungen",
        "btn_ok": "✅ OK",
        "btn_history": "📜 Verlauf",
        "btn_cancel": "❌ Abbrechen",
        "btn_language": "🌐 Sprache",

        # Database messages
        "history_empty": "Verlauf ist leer 📭",
        "key_default_name": "Schlüssel {port}",
        "database_not_found": "Datenbank nicht gefunden. Erstelle initial keys_db.json...",
        "json_error": "🚨 JSON-Lesefehler! Datei ist beschädigt. Verwende Standardeinstellungen.",
        "error_querying": "Fehler beim Abfragen des Schalters:",
        "key_inserted": "Eingesetzt 🟢",
        "key_missing": "Fehlt 🔴",
        "network_error": "Netzwerkfehler:",
        "bot_started": "Bot gestartet mit sauberem Chat und ereignisgesteuert Benutzeroberfläche...",
        "alert_pushed": "Benachrichtigung gesendet:",

        # Language names
        "lang_english": "English",
        "lang_german": "Deutsch",
        "lang_russian": "Русский",
        "lang_ukrainian": "Українська",

        # Language selection
        "select_language": "Bitte wählen Sie Ihre Sprache:",
    },
    "ru": {
        # UI Messages
        "querying_switch": "Опрашиваю свитч... ⏳",
        "current_key_status": "Текущее состояние ключей:\n\n",
        "switch_error": "Ошибка связи со свитчом! ⚠️",
        "access_denied": "⛔️ Доступ запрещен.",
        "returning_to_menu": "Возвращаемся в меню.",
        "recent_events": "Последние события:\n\n",
        "confirm_alert": "⚠️ Пожалуйста, подтвердите прочтение алерта!",
        "action_cancelled": "Действие отменено.",
        "port_selected": "Выбран порт {port}. Введи новое имя:",
        "select_port": "Выбери порт 2-7 или жми Отмена.",
        "key_renamed": "✅ Ключ на порту {port} теперь: «{name}»",
        "hello": "Привет! Я твоя умная ключница.",
        "which_port": "Какой порт переименовать?",
        "command_not_recognized": "Команда не распознана. Используй меню 👇",
        "alert_message": "⚠️ ВНИМАНИЕ! ИЗМЕНЕНИЕ!\n\n{key_name} (Порт {port}): {status}",
        "unauthorized_attempt": "Несанкционированная попытка:",

        # Menu buttons
        "btn_key_status": "🔄 Статус ключей",
        "btn_settings": "⚙️ Настройки",
        "btn_ok": "✅ OK",
        "btn_history": "📜 История",
        "btn_cancel": "❌ Отмена",
        "btn_language": "🌐 Язык",

        # Database messages
        "history_empty": "История пуста 📭",
        "key_default_name": "Ключ {port}",
        "database_not_found": "База данных не найдена. Создаю initial keys_db.json...",
        "json_error": "🚨 Ошибка чтения JSON! Файл повреждён. Использую стандартные настройки.",
        "error_querying": "Ошибка при опросе свитча:",
        "key_inserted": "Вставлен 🟢",
        "key_missing": "Отсутствует 🔴",
        "network_error": "Ошибка сети:",
        "bot_started": "Бот запущен с функцией Чистого чата и событийным интерфейсом...",
        "alert_pushed": "Алерт отправлен:",

        # Language names
        "lang_english": "English",
        "lang_german": "Deutsch",
        "lang_russian": "Русский",
        "lang_ukrainian": "Українська",

        # Language selection
        "select_language": "Пожалуйста, выберите язык:",
    },
    "uk": {
        # UI Messages
        "querying_switch": "Запит до комутатора... ⏳",
        "current_key_status": "Поточний стан ключів:\n\n",
        "switch_error": "Помилка комунікації з комутатором! ⚠️",
        "access_denied": "⛔️ Доступ заборонено.",
        "returning_to_menu": "Повертаємось до меню.",
        "recent_events": "Останні події:\n\n",
        "confirm_alert": "⚠️ Будь ласка, підтвердіть, що ви прочитали сповіщення!",
        "action_cancelled": "Дію скасовано.",
        "port_selected": "Порт {port} вибрано. Введіть нову назву:",
        "select_port": "Виберіть порт 2-7 або натисніть Скасувати.",
        "key_renamed": "✅ Ключ на порту {port} тепер: «{name}»",
        "hello": "Привіт! Я твій розумний хранитель ключів.",
        "which_port": "Який порт перейменувати?",
        "command_not_recognized": "Команда не розпізнана. Використовуйте меню внизу 👇",
        "alert_message": "⚠️ УВАГА! ЗМІНА СТАНУ!\n\n{key_name} (Порт {port}): {status}",
        "unauthorized_attempt": "Несанкціонована спроба:",

        # Menu buttons
        "btn_key_status": "🔄 Стан ключів",
        "btn_settings": "⚙️ Налаштування",
        "btn_ok": "✅ OK",
        "btn_history": "📜 Історія",
        "btn_cancel": "❌ Скасувати",
        "btn_language": "🌐 Мова",

        # Database messages
        "history_empty": "Історія порожня 📭",
        "key_default_name": "Ключ {port}",
        "database_not_found": "Базу даних не знайдено. Створюю initial keys_db.json...",
        "json_error": "🚨 Помилка читання JSON! Файл пошкоджено. Використовую стандартні налаштування.",
        "error_querying": "Помилка при запиті до комутатора:",
        "key_inserted": "Встановлено 🟢",
        "key_missing": "Відсутній 🔴",
        "network_error": "Помилка мережі:",
        "bot_started": "Бот запущено з функцією чистого чату та подієм керованим інтерфейсом...",
        "alert_pushed": "Сповіщення відправлено:",

        # Language names
        "lang_english": "English",
        "lang_german": "Deutsch",
        "lang_russian": "Русский",
        "lang_ukrainian": "Українська",

        # Language selection
        "select_language": "Будь ласка, виберіть мову:",
    }
}

# Current language (default: English)
current_language = "en"

def set_language(lang_code: str):
    """Set the current language."""
    global current_language
    if lang_code in TRANSLATIONS:
        current_language = lang_code
        return True
    return False

def get_language():
    """Get the current language code."""
    return current_language

def get_available_languages():
    """Get list of available language codes."""
    return list(TRANSLATIONS.keys())

def t(key: str, **kwargs) -> str:
    """
    Get translated text for the given key.
    Supports string formatting with kwargs.
    Example: t("key_renamed", port=5, name="MyKey")
    """
    if current_language not in TRANSLATIONS:
        current_lang = "en"
    else:
        current_lang = current_language

    translation = TRANSLATIONS[current_lang].get(key, f"[{key}]")

    if kwargs:
        try:
            return translation.format(**kwargs)
        except KeyError:
            return translation

    return translation

def get_language_name(lang_code: str) -> str:
    """Get the display name of a language."""
    lang_key = f"lang_{lang_code}"
    return TRANSLATIONS["en"].get(lang_key, lang_code)

