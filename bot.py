# -*- coding: utf-8 -*-
"""
MinterShopBot 1.7

ГЛАВНОЕ: одновременно может работать ТОЛЬКО ОДИН процесс с этим токеном.
Если в логах Conflict / getUpdates — где-то крутится вторая копия бота.
"""
from __future__ import annotations

import asyncio
import atexit
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, Optional, TextIO

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from aiogram import Bot, Dispatcher, BaseMiddleware
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import TelegramObject, Message, CallbackQuery, Update

from config import BOT_TOKEN, OWNER_IDS, ADMIN_IDS, ENV_FILE, DATA_DIR
from storage import is_blacklisted
from handlers.start import router as start_router, setup_bot_commands
from handlers.menu import router as menu_router
from handlers.checks import router as checks_router
from handlers.settings import router as settings_router

# ─── single-instance lock ────────────────────────────────────
_lock_fh: Optional[TextIO] = None


def acquire_singleton_lock() -> None:
    """
    Файл-лок data/bot.lock — второй процесс на ТОМ ЖЕ диске не запустится.
    Если два контейнера с разными ФС — лок не поможет: оставь 1 реплику на хостинге.
    """
    global _lock_fh
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    lock_path = DATA_DIR / "bot.lock"
    _lock_fh = open(lock_path, "a+", encoding="utf-8")
    try:
        import fcntl
        fcntl.flock(_lock_fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("=" * 60)
        print("СТОП: бот УЖЕ запущен (data/bot.lock занят).")
        print("Закрой второй процесс / вторую реплику на хостинге.")
        print("Иначе будет Conflict и кнопки/команды «через раз».")
        print("=" * 60)
        sys.exit(1)
    except ImportError:
        # Windows fallback — не жёсткий
        pass
    _lock_fh.seek(0)
    _lock_fh.truncate()
    _lock_fh.write(f"pid={os.getpid()} started={time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    _lock_fh.flush()

    def _release() -> None:
        global _lock_fh
        if _lock_fh is None:
            return
        try:
            import fcntl
            fcntl.flock(_lock_fh.fileno(), fcntl.LOCK_UN)
        except Exception:
            pass
        try:
            _lock_fh.close()
        except Exception:
            pass
        _lock_fh = None

    atexit.register(_release)


class BlacklistMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)
        if not is_blacklisted(user.id):
            return await handler(event, data)

        text = ""
        if isinstance(event, Update) and event.message:
            text = (event.message.text or "").strip().lower()
        elif isinstance(event, Message):
            text = (event.text or "").strip().lower()

        if text.startswith("/appeal"):
            return await handler(event, data)

        if isinstance(event, Update) and event.callback_query:
            try:
                await event.callback_query.answer()
            except Exception:
                pass
            return None
        if isinstance(event, CallbackQuery):
            try:
                await event.answer()
            except Exception:
                pass
            return None
        return None


class ConflictLogFilter(logging.Filter):
    """Раз в N секунд напоминаем про второй инстанс."""

    def __init__(self) -> None:
        super().__init__()
        self._last = 0.0

    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if "Conflict" in msg or "terminated by other getUpdates" in msg:
            now = time.time()
            if now - self._last > 15:
                self._last = now
                print(
                    "\n!!! CONFLICT: работает ЕЩЁ ОДИН бот с этим же токеном.\n"
                    "!!! Останови все лишние процессы/реплики/старые деплои.\n"
                    "!!! Пока их два — /menu и кнопки будут отваливаться.\n",
                    flush=True,
                )
        return True


async def main() -> None:
    acquire_singleton_lock()

    if not BOT_TOKEN or BOT_TOKEN.startswith("123456"):
        print("Укажи BOT_TOKEN в config.env")
        print(f"Файл: {ENV_FILE}")
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logging.getLogger("aiogram.dispatcher").addFilter(ConflictLogFilter())

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("[+] webhook сброшен, pending updates очищены")
    except Exception as e:
        print(f"[!] delete_webhook: {e}")

    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(BlacklistMiddleware())

    dp.include_router(start_router)
    dp.include_router(settings_router)
    dp.include_router(checks_router)
    dp.include_router(menu_router)

    await setup_bot_commands(bot)

    me = await bot.get_me()
    print(f"[+] MinterShopBot 1.7 | @{me.username} (id={me.id})")
    print(f"[+] PID={os.getpid()} | lock={DATA_DIR / 'bot.lock'}")
    print(f"[+] Owners: {sorted(OWNER_IDS) or '—'}")
    print("[!] Если в логе Conflict — где-то крутится ВТОРАЯ копия бота. Убей её.")

    await dp.start_polling(bot, allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    asyncio.run(main())
