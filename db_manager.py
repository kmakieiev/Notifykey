import json
import os

DB_FILE = "keys_db.json"

# Дефолтная схема для первого запуска, если файла еще нет
DEFAULT_DB = {
    "2": {"name": "Ключ 2"},
    "3": {"name": "Ключ 3"},
    "4": {"name": "Ключ 4"},
    "5": {"name": "Ключ 5"},
    "6": {"name": "Ключ 6"},
    "7": {"name": "Ключ 7"}
}


def load_keys():
    """Загружает базу ключей из JSON. Если файла нет - создает дефолтную."""
    # Проверяем, существует ли файл физически
    if not os.path.exists(DB_FILE):
        print("База данных не найдена. Создаю стартовый keys_db.json...")
        save_keys(DEFAULT_DB)
        return dict(DEFAULT_DB)  # Возвращаем копию дефолтного словаря

    # Пытаемся прочитать файл
    try:
        with open(DB_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except json.JSONDecodeError:
        # Страховка на случай, если при сохранении моргнул свет и JSON сломался
        print("🚨 Ошибка чтения JSON! Файл поврежден. Возвращаю дефолтные настройки.")
        return dict(DEFAULT_DB)


def save_keys(data):
    """Сохраняет словарь в JSON файл."""
    with open(DB_FILE, "w", encoding="utf-8") as file:
        # ensure_ascii=False нужен, чтобы русские буквы не превращались в кракозябры вроде \u041a
        # indent=4 делает файл красивым и читаемым для человека (с отступами)
        json.dump(data, file, ensure_ascii=False, indent=4)