# -*- coding: utf-8 -*-
"""MinterShopBot 1.2"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, OWNER_IDS, ADMIN_IDS
from handlers.middlewares import BlacklistMiddleware
from handlers.start import router as start_router
from handlers.menu import router as menu_router
from handlers.checks import router as checks_router
from handlers.settings import router as settings_router


async def main() -> None:
    if not BOT_TOKEN or BOT_TOKEN.startswith("123456"):
        print("Укажи BOT_TOKEN в config.env")
        sys.exit(1)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(BlacklistMiddleware())

    dp.include_router(start_router)
    dp.include_router(settings_router)
    dp.include_router(checks_router)
    dp.include_router(menu_router)

    me = await bot.get_me()
    print(f"[+] MinterShopBot 1.2 | @{me.username}")
    print(f"[+] Owners: {sorted(OWNER_IDS) or '—'} | Admins: {sorted(ADMIN_IDS) or '—'}")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
