# -*- coding: utf-8 -*-
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# Стикер после /start: либо file_id из Telegram, либо локальный файл
START_STICKER_ID = os.getenv("START_STICKER_ID", "").strip()
START_STICKER_FILE = os.getenv("START_STICKER_FILE", "").strip()

WEBAPP_URL = os.getenv("WEBAPP_URL", "https://example.com/app").strip()
FRAGMENT_URL = os.getenv("FRAGMENT_URL", "https://fragment.com").strip()

WELCOME_PHOTO = BASE_DIR / "media" / "welcome.jpg"

# Текст приветствия (как в оригинале, чуть вычищен от «смешанных» букв)
WELCOME_TEXT = (
    "🫰 Привет! Это удобный бот для покупки/передачи звёзд в Telegram.\n"
    "\n"
    "\n"
    "С помощью него можно моментально покупать и передавать звёзды.\n"
    "\n"
    "Бот работает почти год, и с помощью него куплена большая доля звёзд в Telegram.\n"
    "\n"
    "\n"
    "С помощью бота куплено:\n"
    "7,357,760 ⭐️ (~ $110,366)"
)

# Простая in-memory «БД» (user_id -> баланс). Для продакшена замени на SQLite/Postgres.
USERS: dict[int, dict] = {}


def get_user(user_id: int) -> dict:
    if user_id not in USERS:
        USERS[user_id] = {
            "stars": 0.0,
            "dust": 0.0,
            "ref": 0.0,
            "purchases": 0,
            "autobuy": False,
        }
    return USERS[user_id]
