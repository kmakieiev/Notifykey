# 🗝️ Smart Keykeeper (NotifyKey)

A lightweight, background Python daemon running on a Raspberry Pi that monitors the physical presence of keys (RJ45 loopback plugs) using an HP ProCurve switch and SNMP. It communicates via a Telegram bot using pure HTTP API and Long Polling—no heavy frameworks attached.

Built with a strong focus on understanding fundamental networking, hardware-to-software bridging, and bare-metal API interactions.

## ✨ Features

* **Real-time Hardware Monitoring:** Uses UNIX `snmpwalk` to track port states (Up/Down) directly from the OS level, avoiding black-box SNMP libraries.
* **Proactive Alerts (Push Mode):** Maintains an internal state machine to compute diffs. Instantly notifies the administrator when a key is extracted or returned.
* **On-Demand Status (Pull Mode):** Responds to `/status` commands in Telegram with a real-time parsed summary of all key slots.
* **Zero-Magic Framework:** The Telegram Long Polling cycle is built entirely from scratch using the `requests` library and manual JSON parsing.
* **🌍 Multi-Language Support:** Full localization in 4 languages - English, German, Russian, and Ukrainian with seamless language switching and automatic persistence.

## 🛠️ Hardware Topography

* **Server:** Raspberry Pi 4B (8GB)
* **Network Switch:** HP ProCurve 1800-8G (J9029A)
* **Physical Keys:** Custom-made RJ45 loopback plugs (bridged pins 1-3 and 2-6).
* **Port Allocation:**
  * **Port 1:** Router (Uplink / Infrastructure)
  * **Ports 2-7:** Active Key Slots
  * **Port 8:** Raspberry Pi (Daemon host)
* **L2 Security:** To prevent broadcast storms when loopbacks are inserted, key ports are strictly isolated (one port = one VLAN) and port speeds are manually downgraded to `100FDX` (Auto-negotiation disabled).

## 🏗️ Project Architecture

### Core Components

The project consists of 6 main Python modules:

* **`localization.py`** - Multi-language translation system
  * 4 fully translated languages (EN, DE, RU, UK)
  * 160+ translated strings
  * Simple `t()` function for accessing translations
  * Language persistence mechanism

* **`config.py`** - Configuration & dynamic UI
  * Telegram API configuration
  * Dynamic menu builders that adapt to current language
  * Keyboard layouts for all UI states

* **`db_manager.py`** - Database & persistence
  * Saves/loads key names and configurations (JSON-based)
  * Manages language preferences
  * Maintains event history log (last 10 events)

* **`tg_api.py`** - Telegram API wrapper
  * Long Polling implementation for receiving updates
  * Message sending with keyboard support
  * Message deletion for "Clean Chat" functionality

* **`snmp_scanner.py`** - Hardware monitoring
  * SNMP queries to HP switch (using `snmpwalk`)
  * Parses port status (Up/Down)
  * Filters to ports 2-7 only

* **`main.py`** - Bot orchestration
  * Event-driven state machine
  * Language selection handler
  * Background hardware monitoring loop
  * Alert system for state changes

### Data Flow

```
SNMP Queries (snmp_scanner.py)
        ↓
State Change Detection (main.py)
        ↓
Alert + History Log (db_manager.py)
        ↓
Telegram Notification (tg_api.py)
        ↓
Localized Message (localization.py)
        ↓
User receives alert in their language
```

## 🌍 Multi-Language Localization

The bot fully supports **4 languages** with seamless switching:

### Supported Languages
- 🇬🇧 **English** (en) - Default
- 🇩🇪 **German** (de) - Deutsch
- 🇷🇺 **Russian** (ru) - Русский
- 🇺🇦 **Ukrainian** (uk) - Українська

### How It Works

1. **Language Selection:** User clicks "🌐 Language" button in Telegram
2. **Instant Updates:** All menus and messages update immediately
3. **Automatic Persistence:** Selection saved to `language.json`
4. **Restored on Restart:** Preference loaded on bot startup

### Translation Coverage

- ✅ All UI messages (20+ keys)
- ✅ Menu buttons (6 keys)
- ✅ Database messages (5+ keys)
- ✅ Alert messages (4+ keys)
- ✅ Language names (4 keys)

**Total: 40+ translation keys × 4 languages = 160+ translated strings**

### Using Translations in Code

```python
from localization import t

# Simple lookup
message = t("hello")

# With parameters
message = t("key_renamed", port=5, name="Front Door")

# Change language
from localization import set_language
from db_manager import save_language

set_language("de")
save_language("de")
```

## 🚀 Installation & Setup

### 1. System Requirements (Debian/Raspberry Pi OS)
The script relies on native UNIX SNMP utilities. Install them via terminal:
```bash
sudo apt update && sudo apt install snmp
```

### 2. Clone the Repository

```bash
git clone [https://github.com/kmakieiev/NotifyKey.git](https://github.com/kmakieiev/NotifyKey.git)
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

Create a `.env` file in the root directory to store your credentials securely:

```env
TELEGRAM_TOKEN=your_botfather_token_here
ADMIN_ID=your_personal_telegram_chat_id
```

### 5. Database Files (Auto-Created)

On first run, the bot creates:
- `keys_db.json` - Stores key names for ports 2-7
- `language.json` - Stores user's language preference (defaults to English)
- `history.json` - Maintains last 10 events

## ⚙️ Usage

### Running the Bot

```bash
python main.py
```

The bot will:
1. Load saved language preference (or default to English)
2. Connect to SNMP switch
3. Start Long Polling for Telegram updates
4. Begin background hardware monitoring

### Telegram Commands & Buttons

**Commands:**
- `/start` - Initialize bot connection (shows main menu)
- `/status` - Get current key status

**Main Menu Buttons:**
- 🔄 **Key Status** - Query switch and show all ports status
- ⚙️ **Settings** - Rename keys on ports 2-7
- 🌐 **Language** - Change bot language (EN/DE/RU/UK)

**Alert Menu (when key inserted/removed):**
- ✅ **OK** - Acknowledge alert
- 📜 **History** - Show last 10 events

### Renaming Keys

1. Click **⚙️ Settings**
2. Select port (2-7)
3. Enter new name (e.g., "Front Door")
4. Name is saved and used in all future messages

## 📊 File Structure

```
Notifykey/
├── localization.py          # Multi-language translation system
├── config.py                # Configuration & dynamic menus
├── db_manager.py            # Database & persistence (JSON-based)
├── tg_api.py                # Telegram API wrapper
├── snmp_scanner.py          # SNMP hardware monitoring
├── main.py                  # Bot orchestration & state machine
├── .env                     # Telegram credentials (not in repo)
├── keys_db.json             # Key names (auto-created)
├── language.json            # Language preference (auto-created)
└── history.json             # Event history (auto-created)
```

## 🔄 Bot State Machine

The bot uses a state-machine approach for user interactions:

```
IDLE STATE
  ├─ /start → Show main menu
  ├─ 🔄 Status → Query switch + show results
  ├─ ⚙️ Settings → WAITING_FOR_PORT
  └─ 🌐 Language → WAITING_FOR_LANGUAGE

WAITING_FOR_PORT
  └─ Select 2-7 → WAITING_FOR_NAME

WAITING_FOR_NAME
  └─ Enter name → Save + return to IDLE

WAITING_FOR_LANGUAGE
  └─ Select language → Save + return to IDLE

WAITING_FOR_ALERT_ACK (Priority State)
  ├─ ✅ OK → Return to IDLE
  ├─ 📜 History → Show events + return to IDLE
  └─ Other input → Repeat alert (must confirm)
```

**Key Feature:** Alert state is PRIORITY—user cannot do anything else until they acknowledge the alert.

## 🧹 Clean Chat Feature

All user messages are automatically deleted after processing. Only bot messages remain visible in the chat, keeping the interface clean and organized.

## 📝 Event Logging

The bot maintains a history of key state changes:
- Timestamp
- Key name
- New status (Inserted/Missing)
- Last 10 events stored

Access via "📜 History" button when an alert occurs.

## 🔐 Security

- Admin-only access (verified via `ADMIN_ID`)
- Credentials stored in `.env` (never committed)
- SNMP queries read-only (no configuration changes)
- Telegram Long Polling (no webhooks)

## 📈 Performance

- **Hardware Polling:** Every 0.1 seconds (minimal CPU impact)
- **Telegram Updates:** 3-second timeout on Long Polling
- **Memory Usage:** ~5-10 MB (Python + libraries)
- **State Transitions:** Instantaneous

## 🚀 Future Enhancements

- [ ] Multiple admin support
- [ ] Email notifications
- [ ] SMS alerts
- [ ] Web dashboard
- [ ] More language support
- [ ] Port configuration via UI

## 📄 License

This project is provided as-is for educational and personal use.

## 👤 Author

Created as a learning project focusing on:
- Bare-metal API integration (no frameworks)
- SNMP hardware interaction
- Telegram bot development
- State machine design patterns
- Multi-language localization
