# -*- coding: utf-8 -*-
"""
MinterShopBot 1.1 — настройки из config.env
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "config.env"


def _load_env(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        os.environ.setdefault(key, val)


_load_env(ENV_FILE)

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()


def _parse_ids(raw: str) -> set[int]:
    out: set[int] = set()
    for part in (raw or "").replace(";", ",").split(","):
        part = part.strip()
        if part.isdigit():
            out.add(int(part))
    return out


OWNER_IDS = _parse_ids(os.getenv("OWNER_IDS", ""))
ADMIN_IDS = _parse_ids(os.getenv("ADMIN_IDS", "")) | OWNER_IDS

# Стикер после стартового сообщения (зашит в код)
START_STICKER_ID = "CAACAgIAAxkBAAESBtlqy-s578eyuGb03MbzkdqsSvoj0AACiwADr8ZRGpyZPDhzkQUEPQQ"

WELCOME_PHOTO = BASE_DIR / "media" / "welcome.jpg"

# Premium custom emoji: <tg-emoji emoji-id="...">fallback</tg-emoji>
def e(emoji_id: str, fallback: str = "•") -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


WELCOME_TEXT = (
    f"{e('5267263603081224506', '✨')} Добро пожаловать в MinterShop!\n"
    f"\n"
    f"{e('5267298473920700985', '💫')} Твой удобный помощник для покупки и передачи Telegram Stars.\n"
    f"\n"
    f"{e('5188481279963715781', '📋')} Что умеет наш бот:\n"
    f"・ Покупка звёзд в пару нажатий\n"
    f"・ Удобная передача звёзд друзьям через чеки\n"
    f"・ Быстрое оформление заказа\n"
    f"\n"
    f"{e('5231200819986047254', '📊')} Статистика бота:\n"
    f"{e('5954317306535351574', '⭐')} Уже куплено: ~ 12 947 звёзд\n"
    f"{e('5409048419211682843', '💰')} Общая сумма: ~ 17 866 ₽\n"
    f"\n"
    f"{e('5402186569006210455', '📈')} Текущий курс:\n"
    f"{e('5967512159033234930', '⭐')} 1 звезда = 1,38 ₽\n"
    f"\n"
    f"Выбирай нужное действие в меню ниже и пользуйся с удовольствием! "
    f"{e('5427168083074628963', '❤️')}"
)

# In-memory users (позже — БД)
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


def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS or user_id in OWNER_IDS
