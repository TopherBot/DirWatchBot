#!/usr/bin/env python3
"""DirWatchBot – tiny directory watcher with Telegram notifications.

Author: TopherBot <topherbot@proton.me>
License: MIT (see LICENSE)
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import Final

from dotenv import load_dotenv
from watchdog.events import FileSystemEventHandler, FileSystemEvent
from watchdog.observers import Observer
from telegram import Bot
from telegram.error import TelegramError

# ---------------------------------------------------------------------------
# Configuration & Logging
# ---------------------------------------------------------------------------
load_dotenv()  # Load .env if present

TELEGRAM_TOKEN: Final[str] = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID: Final[str] = os.getenv("TELEGRAM_CHAT_ID", "")
LOG_FILE: Final[str | None] = os.getenv("LOG_FILE")
LOG_LEVEL: Final[int] = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO)

if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
    sys.stderr.write("[ERROR] TELEGRAM_TOKEN and TELEGRAM_CHAT_ID must be set in the environment.\n")
    sys.exit(1)

# Configure the root logger
log_formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
root_logger = logging.getLogger()
root_logger.setLevel(LOG_LEVEL)

stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_formatter)
root_logger.addHandler(stream_handler)

if LOG_FILE:
    from logging.handlers import RotatingFileHandler

    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=1_048_576, backupCount=3)
    file_handler.setFormatter(log_formatter)
    root_logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Telegram Notification Helper
# ---------------------------------------------------------------------------
bot = Bot(token=TELEGRAM_TOKEN)


def send_telegram_message(message: str) -> None:
    """Send *message* to the configured chat.
    Errors are logged but do not crash the watcher.
    """
    try:
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        logger.debug("Sent Telegram message: %s", message)
    except TelegramError as exc:
        logger.error("Failed to send Telegram message: %s", exc)

# ---------------------------------------------------------------------------
# Watchdog Event Handler
# ---------------------------------------------------------------------------
class NotifyingEventHandler(FileSystemEventHandler):
    """Handle filesystem events and forward them to Telegram.
    Only the most common events are reported to keep noise low.
    """

    def on_created(self, event: FileSystemEvent) -> None:
        self._notify(event, "created")

    def on_modified(self, event: FileSystemEvent) -> None:
        self._notify(event, "modified")

    def on_deleted(self, event: FileSystemEvent) -> None:
        self._notify(event, "deleted")

    def on_moved(self, event: FileSystemEvent) -> None:
        # event has src_path and dest_path
        src = Path(event.src_path)
        dest = Path(event.dest_path)
        message = f"🛫 Moved: {src} → {dest}"
        logger.info(message)
        send_telegram_message(message)

    def _notify(self, event: FileSystemEvent, action: str) -> None:
        if event.is_directory:
            typ = "directory"
        else:
            typ = "file"
        path = Path(event.src_path)
        message = f"📁 {typ.capitalize()} {action}: {path}"
        logger.info(message)
        send_telegram_message(message)

# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------
def main() -> None:
    if len(sys.argv) != 2:
        sys.stderr.write(f"Usage: {Path(sys.argv[0]).name} <path-to-watch>\n")
        sys.exit(2)

    watch_path = Path(sys.argv[1]).expanduser().resolve()
    if not watch_path.is_dir():
        sys.stderr.write(f"[ERROR] '{watch_path}' is not a valid directory.\n")
        sys.exit(1)

    logger.info("Starting DirWatchBot – watching: %s", watch_path)
    send_telegram_message(f"🚀 DirWatchBot started watching `{watch_path}`")

    event_handler = NotifyingEventHandler()
    observer = Observer()
    observer.schedule(event_handler, str(watch_path), recursive=True)
    observer.start()

    try:
        while True:
            # Keep the main thread alive – guard against KeyboardInterrupt
            observer.join(1)
    except KeyboardInterrupt:
        logger.info("Interrupted by user – shutting down.")
        send_telegram_message("🛑 DirWatchBot stopped by user.")
    finally:
        observer.stop()
        observer.join()
        logger.info("Observer terminated.")


if __name__ == "__main__":
    main()
