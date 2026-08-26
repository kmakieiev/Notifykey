import os
from dotenv import load_dotenv
from localization import t

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Fail-safe check for missing credentials
if not TOKEN or not ADMIN_ID:
    print("🚨 Error: Telegram token or Admin ID not found in .env file!")
    exit(1)

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# Dynamic menu builder functions that use current language
def get_main_menu():
    """Build main menu with current language."""
    return {
        "keyboard": [
            [{"text": t("btn_key_status")}],
            [{"text": t("btn_settings")}],
            [{"text": t("btn_language")}]
        ],
        "resize_keyboard": True,
        "is_persistent": True
    }

def get_alert_menu():
    """Build alert menu with current language."""
    return {
        "keyboard": [
            [{"text": t("btn_ok")}, {"text": t("btn_history")}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": True
    }

def get_language_menu():
    """Build language selection menu."""
    from localization import get_available_languages, get_language_name
    languages = get_available_languages()
    keyboard = [[{"text": get_language_name(lang)}] for lang in languages]
    return {
        "keyboard": keyboard,
        "resize_keyboard": True,
        "one_time_keyboard": True
    }
