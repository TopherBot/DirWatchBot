# DirWatchBot

**DirWatchBot** is a *tiny* cross‑platform Python script that monitors a directory (or a set of files) and notifies you via Telegram when anything is created, modified, or deleted.

## Features
- Uses the fast and reliable `watchdog` library.
- Minimal, clean, and type‑annotated code.
- Robust logging to console and optional rotating log file.
- One‑line configuration through environment variables or a `.env` file.
- Zero‑dependency runtime apart from `watchdog` and `python‑telegram-bot` (both installable via `pip`).

## Quick Start
```bash
# Clone the repo (or copy the single file)
git clone https://github.com/yourname/DirWatchBot.git && cd DirWatchBot

# Install dependencies in a virtual environment
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Create a .env file (see below for details)
cp .env.example .env

# Run the watcher
python dirwatchbot.py /path/to/watch
```

## Configuration (`.env`)
| Variable | Description | Example |
|---|---|---|
| `TELEGRAM_TOKEN` | Bot token obtained from @BotFather. | `123456789:AA...` |
| `TELEGRAM_CHAT_ID` | Chat ID where notifications should be sent. Use `@userinfobot` to get yours. | `-987654321` |
| `LOG_FILE` *(optional)* | Path to a rotating log file. If omitted, logs go only to stdout. | `dirwatch.log` |
| `LOG_LEVEL` *(optional)* | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). | `INFO` |

## How It Works
1. The script starts a `watchdog.Observer` on the target directory.
2. Every filesystem event triggers a formatted message.
3. The message is sent through the Telegram Bot API.
4. All events are logged with timestamps for auditability.

## License
MIT – see the `LICENSE` file.

---
*Happy coding!* 🎉