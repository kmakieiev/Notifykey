import subprocess
from localization import t


def get_keys_status():
    """Queries the switch via SNMP and returns a dictionary with key statuses (ports 2-7 only)."""

    command = [
        "snmpwalk", "-v", "2c", "-c", "public",
        "192.168.0.211", "1.3.6.1.2.1.2.2.1.8"
    ]

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        raw_output = result.stdout
    except subprocess.CalledProcessError as e:
        print(f"{t('error_querying')} {e}")
        return None

    keys_status = {}

    for line in raw_output.strip().split('\n'):
        if "INTEGER:" in line:
            oid_part, val_part = line.split("=")

            oid = oid_part.strip()
            port_index = oid.split(".")[-1]

            value = int(val_part.split(":")[1].strip())

            # We're interested only in HP ports (5001 - 5008)
            if port_index.startswith("500") and len(port_index) == 4:
                port_num = int(port_index) - 5000

                # Filter infrastructure: keep STRICTLY ports 2 through 7
                if 2 <= port_num <= 7:
                    # 1 = Up (Key in place), 2 = Down (Key removed)
                    if value == 1:
                        keys_status[port_num] = t("key_inserted")
                    else:
                        keys_status[port_num] = t("key_missing")

    return keys_status


# Block for independent testing
if __name__ == "__main__":
    status = get_keys_status()
    if status:
        print(t("current_key_status"))
        for port, state in sorted(status.items()):
            print(f"Key {port}: {state}")
