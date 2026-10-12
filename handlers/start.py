# -*- coding: utf-8 -*-
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext

from config import START_STICKER_ID, START_PHOTO, WELCOME_TEXT, is_owner
from keyboards import main_menu
from storage import get_user

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.clear()
    get_user(message.from_user.id)

    if START_PHOTO.exists():
        await message.answer_photo(
            photo=FSInputFile(START_PHOTO),
            caption=WELCOME_TEXT,
            reply_markup=main_menu(),
        )
    else:
        await message.answer(WELCOME_TEXT, reply_markup=main_menu())

    try:
        await message.answer_sticker(START_STICKER_ID)
    except Exception:
        pass


@router.message(Command("appeal"))
async def cmd_appeal(message: Message) -> None:
    await message.answer(
        "📨 Апелляция принята в обработку.\n"
        "Опишите ситуацию одним сообщением — администрация рассмотрит заявку."
    )
