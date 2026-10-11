# -*- coding: utf-8 -*-
from pathlib import Path

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile, BufferedInputFile

from config import (
    START_STICKER_ID,
    START_STICKER_FILE,
    WELCOME_PHOTO,
    WELCOME_TEXT,
    get_user,
    BASE_DIR,
)
from keyboards import main_menu

router = Router()


async def send_start_sticker(message: Message) -> None:
    """Отправляет стикер после /start, если настроен."""
    if START_STICKER_ID:
        try:
            await message.answer_sticker(START_STICKER_ID)
            return
        except Exception:
            pass

    if START_STICKER_FILE:
        path = Path(START_STICKER_FILE)
        if not path.is_absolute():
            path = BASE_DIR / path
        if path.exists():
            try:
                await message.answer_sticker(FSInputFile(path))
                return
            except Exception:
                pass


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    get_user(message.from_user.id)

    # 1) Стикер (как в оригинале — первым)
    await send_start_sticker(message)

    # 2) Фото + текст + главное меню
    caption = WELCOME_TEXT
    if WELCOME_PHOTO.exists():
        await message.answer_photo(
            photo=FSInputFile(WELCOME_PHOTO),
            caption=caption,
            reply_markup=main_menu(),
        )
    else:
        await message.answer(
            caption,
            reply_markup=main_menu(),
        )
