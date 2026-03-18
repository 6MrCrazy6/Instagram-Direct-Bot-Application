# Gravity — Instagram Direct Bot 🚀

An automated solution for sending Instagram Direct messages with **KeyCRM** integration. The bot extracts contacts from your CRM system, finds them on Instagram, and sends personalized messages using human-like behavior emulation.

---

## 🌟 Key Features

- **KeyCRM Integration**: Automatically collect contacts (Instagram accounts) from the KeyCRM sales funnel.
- **Smart Filtering**: The bot processes only valid contacts with provided Instagram links.
- **Human Emulation**: Utilizes `undetected-chromedriver` and "human-like" typing functions to minimize the risk of account restrictions.
- **Graphical User Interface (GUI)**: User-friendly application window for management (start, pause, logging, settings).
- **Logging System**: Real-time reporting of every bot action, with logs saved to a local file.
- **Flexible Settings**: Change Instagram accounts and API keys directly through the interface.

---

## 🛠 Tech Stack

- **Language**: Python 3.10+
- **Libraries**: 
  - `Selenium` + `undetected-chromedriver` (browser automation)
  - `Tkinter` (graphical interface)
  - `Requests` (KeyCRM API interaction)
  - `Pandas` (data processing)
  - `Python-dotenv` (configuration management)

---

## 📂 Project Structure

```text
├── apps_design_interface/  # Graphical User Interface (Tkinter)
│   ├── assets/             # Logos and icons
│   └── gui_main.py         # Main application window
├── services/               # Business logic
│   ├── campaign_manager.py # Queue and CRM data management
│   └── keycrm_service.py   # KeyCRM API client
├── keyes_data/             # Sensitive data
│   └── password_keys_dates.env # Settings (logins, passwords, API keys)
├── main.py                 # Application entry point
├── bot_core.py             # Browser control core
├── message_sender.py       # Direct message sending logic
├── logger.py               # Logging system
├── utils.py                # Helper functions
└── requirements.txt        # List of dependencies
```

---

## 🚀 Quick Start

### 1. Environment Setup
Ensure you have Python 3.10 or higher installed. Clone the repository and install the dependencies:

```bash
git clone https://github.com/6MrCrazy6/Instagram-Direct-Bot-Application.git
cd Instagram-Direct-Bot-Application
pip install -r requirements.txt
```

### 2. Configuration
Navigate to the `keyes_data` folder and configure the `password_keys_dates.env` file. You can do this manually or via the "Settings" tab in the application.

Key parameters:
- `INSTAGRAM_USERNAME`: Your Instagram login.
- `INSTAGRAM_PASSWORD`: Your Instagram password.
- `KEYCRM_API_KEY`: Your KeyCRM API key.
- `API_BASE_URL`: KeyCRM API base URL.

### 3. Launch
Run the main script:

```bash
python main.py
```

---

## 🖥 Usage

1. **Authorization**: On the first run, the bot will open a browser window for Instagram login. It is recommended to log in manually if the bot doesn't do it automatically.
2. **Start**: Click the **"▶ Start Campaign"** button. The bot will load data from KeyCRM and begin sending messages sequentially.
3. **Pause**: You can pause the operation at any time using the **"⏸ Pause"** button.
4. **Logs**: The central window displays the current status (successful sends, errors, delays).

---

## ⚠️ Disclaimer

This application was created to automate workflows for **Gravity Smart Home**.

**Important:** Using automation tools on Instagram may violate the platform's Terms of Service. The developers are not responsible for any account restrictions or bans. Use this application at your own risk.

---


## 🤝 Development

Author: [6MrCrazy6](https://github.com/6MrCrazy6)
Developed for internal use at **Gravity**.
