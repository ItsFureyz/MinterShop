# -*- coding: utf-8 -*-
from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, FSInputFile

from config import (
    START_STICKER_ID,
    WELCOME_PHOTO,
    WELCOME_TEXT,
    get_user,
)
from keyboards import main_menu

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    get_user(message.from_user.id)

    # 1) Основное сообщение (фото + текст + меню)
    if WELCOME_PHOTO.exists():
        await message.answer_photo(
            photo=FSInputFile(WELCOME_PHOTO),
            caption=WELCOME_TEXT,
            reply_markup=main_menu(),
        )
    else:
        await message.answer(
            WELCOME_TEXT,
            reply_markup=main_menu(),
        )

    # 2) Стикер после основного сообщения
    try:
        await message.answer_sticker(START_STICKER_ID)
    except Exception:
        pass
