import json
import os
import datetime

HIST_FILE = "history.json"
DB_FILE = "keys_db.json"
HIST_FILE = "history.json"

def log_event(port, name, state):
    """Logs a hardware event with a timestamp."""
    history = []
    if os.path.exists(HIST_FILE):
        with open(HIST_FILE, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except:
                history = []

    timestamp = datetime.datetime.now().strftime("%d.%m %H:%M:%S")
    event = f"[{timestamp}] {name} (Port {port}): {state}"

    # Keep only last 10 events
    history.insert(0, event)
    history = history[:10]

    with open(HIST_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=4)


def get_history():
    """Returns the last logged events as a single string."""
    if not os.path.exists(HIST_FILE):
        return "История пуста 📭"
    with open(HIST_FILE, "r", encoding="utf-8") as f:
        history = json.load(f)
        return "\n".join(history) if history else "История пуста 📭"

# Default schema for the first run if the database file does not exist
DEFAULT_DB = {
    "2": {"name": "Ключ 2"},
    "3": {"name": "Ключ 3"},
    "4": {"name": "Ключ 4"},
    "5": {"name": "Ключ 5"},
    "6": {"name": "Ключ 6"},
    "7": {"name": "Ключ 7"}
}

def load_keys():
    """
    Loads the key database from JSON.
    Creates and returns a default schema if the file is missing.
    """
    if not os.path.exists(DB_FILE):
        print("Database not found. Creating an initial keys_db.json...")
        save_keys(DEFAULT_DB)
        return dict(DEFAULT_DB)

    try:
        with open(DB_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("🚨 JSON Read Error! File is corrupted. Returning default settings.")
        return dict(DEFAULT_DB)


def save_keys(data):
    """
    Saves the provided dictionary into the JSON database file.
    """
    with open(DB_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)