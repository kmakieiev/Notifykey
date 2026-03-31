import subprocess



def get_keys_status():
    """Опрашивает свитч по SNMP и возвращает словарь со статусами ключей (только порты 2-7)."""

    command = [
        "snmpwalk", "-v", "2c", "-c", "public",
        "192.168.0.211", "1.3.6.1.2.1.2.2.1.8"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        raw_output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при опросе свитча: {e}")
        return None

    keys_status = {}

    for line in raw_output.strip().split('\n'):
        if "INTEGER:" in line:
            oid_part, val_part = line.split("=")

            oid = oid_part.strip()
            port_index = oid.split(".")[-1]

            value = int(val_part.split(":")[1].strip())

            # Нас интересуют только порты HP (5001 - 5008)
            if port_index.startswith("500") and len(port_index) == 4:
                port_num = int(port_index) - 5000

                # Фильтруем инфраструктуру: оставляем СТРОГО порты с 2 по 7
                if 2 <= port_num <= 7:
                    # 1 = Up (Ключ на месте), 2 = Down (Ключ забрали)
                    if value == 1:
                        keys_status[port_num] = "Вставлен 🟢"
                    else:
                        keys_status[port_num] = "Отсутствует 🔴"

    return keys_status


# Блок для независимого тестирования
if __name__ == "__main__":
    status = get_keys_status()
    if status:
        print("Текущее состояние ключей (порты 2-7):")
        for port, state in sorted(status.items()):
            print(f"Ключ {port}: {state}")