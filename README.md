# 🗝️ Smart Keykeeper (NotifyKey)

A lightweight, background Python daemon running on a Raspberry Pi that monitors the physical presence of keys (RJ45 loopback plugs) using an HP ProCurve switch and SNMP. It communicates via a Telegram bot using pure HTTP API and Long Polling—no heavy frameworks attached.

Built with a strong focus on understanding fundamental networking, hardware-to-software bridging, and bare-metal API interactions.

## ✨ Features

* **Real-time Hardware Monitoring:** Uses UNIX `snmpwalk` to track port states (Up/Down) directly from the OS level, avoiding black-box SNMP libraries.
* **Proactive Alerts (Push Mode):** Maintains an internal state machine to compute diffs. Instantly notifies the administrator when a key is extracted or returned.
* **On-Demand Status (Pull Mode):** Responds to `/status` commands in Telegram with a real-time parsed summary of all key slots.
* **Zero-Magic Framework:** The Telegram Long Polling cycle is built entirely from scratch using the `requests` library and manual JSON parsing.

## 🛠️ Hardware Topography

* **Server:** Raspberry Pi 4B (8GB)
* **Network Switch:** HP ProCurve 1800-8G (J9029A)
* **Physical Keys:** Custom-made RJ45 loopback plugs (bridged pins 1-3 and 2-6).
* **Port Allocation:**
  * **Port 1:** Router (Uplink / Infrastructure)
  * **Ports 2-7:** Active Key Slots
  * **Port 8:** Raspberry Pi (Daemon host)
* **L2 Security:** To prevent broadcast storms when loopbacks are inserted, key ports are strictly isolated (one port = one VLAN) and port speeds are manually downgraded to `100FDX` (Auto-negotiation disabled).

## 🚀 Installation & Setup

### 1. System Requirements (Debian/Raspberry Pi OS)
The script relies on native UNIX SNMP utilities. Install them via terminal:
```bash
sudo apt update && sudo apt install snmp
```
### 2. Clone the Repository

```bash
git clone [https://github.com/YOUR_USERNAME/NotifyKey.git](https://github.com/YOUR_USERNAME/NotifyKey.git)
cd NotifyKey
```

### 3. Python Environment

It is recommended to run this project in an isolated virtual environment (Python 3.13+).

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests python-dotenv
```

### 4. Environment Variables

Create a .env file in the root directory to store your credentials securely:

```pycon
TELEGRAM_TOKEN=your_botfather_token_here
ADMIN_ID=your_personal_telegram_chat_id
```
## ⚙️ Usage
Run the daemon manually to start the Long Polling cycle:

```bash
python main.py
```

Send ```/start``` to your bot in Telegram to verify connectivity, and ```/status``` to poll the switch.