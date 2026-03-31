import json
import os

DB_FILE = "keys_db.json"

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