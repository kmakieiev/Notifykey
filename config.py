import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

# Fail-safe check for missing credentials
if not TOKEN or not ADMIN_ID:
    print("🚨 Error: Telegram token or Admin ID not found in .env file!")
    exit(1)

BASE_URL = f"https://api.telegram.org/bot{TOKEN}/"

# Persistent main menu layout
MAIN_MENU = {
    "keyboard": [
        [{"text": "🔄 Статус ключей"}],
        [{"text": "⚙️ Настройки"}]
    ],
    "resize_keyboard": True,
    "is_persistent": True
}