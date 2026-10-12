# -*- coding: utf-8 -*-
"""MinterShopBot 1.3"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "config.env"
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)


def _load_env(path: Path) -> dict:
    """Читает config.env. Значения из файла имеют приоритет."""
    data = {}
    if not path.exists():
        return data
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'")
        data[key] = val
        os.environ[key] = val  # всегда из файла
    return data


_ENV = _load_env(ENV_FILE)

BOT_TOKEN = (_ENV.get("BOT_TOKEN") or os.getenv("BOT_TOKEN", "")).strip()


def _parse_ids(raw: str) -> set[int]:
    out: set[int] = set()
    for part in (raw or "").replace(";", ",").split(","):
        part = part.strip()
        if part.isdigit():
            out.add(int(part))
    return out


OWNER_IDS = _parse_ids(_ENV.get("OWNER_IDS") or os.getenv("OWNER_IDS", ""))
ADMIN_IDS = _parse_ids(_ENV.get("ADMIN_IDS") or os.getenv("ADMIN_IDS", "")) | set(OWNER_IDS)


def reload_owners() -> set[int]:
    """Перечитать OWNER_IDS из config.env (на случай правки без рестарта)."""
    global OWNER_IDS, ADMIN_IDS
    env = _load_env(ENV_FILE)
    OWNER_IDS = _parse_ids(env.get("OWNER_IDS", ""))
    ADMIN_IDS = _parse_ids(env.get("ADMIN_IDS", "")) | set(OWNER_IDS)
    return OWNER_IDS

START_STICKER_ID = "CAACAgIAAxkBAAESBtlqy-s578eyuGb03MbzkdqsSvoj0AACiwADr8ZRGpyZPDhzkQUEPQQ"
START_PHOTO = BASE_DIR / "media" / "start.jpg"
DEAL_CHECK_PHOTO = BASE_DIR / "media" / "deal_check.jpg"

RATE_RUB = float(os.getenv("RATE_RUB", "1.34"))
RATE_USD = float(os.getenv("RATE_USD", "0.0149"))
RATE_EUR = float(os.getenv("RATE_EUR", "0.0137"))


def e(emoji_id: str, fallback: str = "•") -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'


def format_money(stars: float) -> str:
    rub = stars * RATE_RUB
    usd = stars * RATE_USD
    eur = stars * RATE_EUR
    return (
        f"{stars:g} ⭐️\n"
        f"≈ {rub:,.2f} ₽  ·  ${usd:,.4f}  ·  €{eur:,.4f}"
    ).replace(",", " ")


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
    f"{e('5954317306535351574', '⭐')} Уже куплено: ~ 71 356 звёзд\n"
    f"{e('5409048419211682843', '💰')} Общая сумма: ~ 95 617 ₽\n"
    f"\n"
    f"{e('5402186569006210455', '📈')} Текущий курс:\n"
    f"{e('5967512159033234930', '⭐')} 1 звезда = {RATE_RUB} ₽"
    f"  ·  ${RATE_USD}  ·  €{RATE_EUR}\n"
    f"\n"
    f"Выберите нужное действие в меню {e('5427168083074628963', '❤️')}"
)

# Тихий ЧС — текст больше не шлём автоматически
BLACKLIST_TEXT = (
    f"{e('5240241223632954241', '⚠️')} Нам очень жаль, что так произошло. "
    f"К сожалению, ваш доступ к боту ограничен. "
    f"Если вы считаете, что это произошло по ошибке, пожалуйста, подайте апелляцию.\n"
    f"\n"
    f"       /appeal"
)


def is_owner(uid: int) -> bool:
    return int(uid) in OWNER_IDS


def is_admin(uid: int) -> bool:
    return int(uid) in ADMIN_IDS or int(uid) in OWNER_IDS
