# -*- coding: utf-8 -*-
"""Команды: быстрый ответ, кэш file_id стартового фото."""
from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, FSInputFile, BotCommand, BotCommandScopeDefault, BotCommandScopeChat
from aiogram.fsm.context import FSMContext

from config import (
    START_STICKER_ID,
    START_PHOTO,
    WELCOME_TEXT,
    OWNER_IDS,
    reload_owners,
)
from keyboards import main_menu, settings_root
from storage import get_user

router = Router(name="commands")

# кэш file_id картинки /start — повторные /menu без загрузки файла
_START_FILE_ID: str | None = None


async def send_main_menu(message: Message, with_sticker: bool = False) -> None:
    global _START_FILE_ID
    get_user(message.from_user.id)

    photo = _START_FILE_ID
    if not photo and START_PHOTO.exists():
        photo = FSInputFile(START_PHOTO)

    if photo:
        msg = await message.answer_photo(
            photo=photo,
            caption=WELCOME_TEXT,
            reply_markup=main_menu(),
        )
        if not _START_FILE_ID and msg.photo:
            _START_FILE_ID = msg.photo[-1].file_id
    else:
        await message.answer(WELCOME_TEXT, reply_markup=main_menu())

    if with_sticker:
        try:
            await message.answer_sticker(START_STICKER_ID)
        except Exception:
            pass


@router.message(Command("start", "menu", "settings", "appeal"))
async def on_command(message: Message, command: CommandObject, state: FSMContext) -> None:
    """Единый хендлер команд — срабатывает и из меню, и при ручном вводе."""
    await state.clear()
    cmd = (command.command or "").lower()
    uid = int(message.from_user.id)
    print(f"[cmd] /{cmd} uid={uid}", flush=True)

    if cmd == "start":
        await send_main_menu(message, with_sticker=True)
        return

    if cmd == "menu":
        await send_main_menu(message, with_sticker=False)
        return

    if cmd == "settings":
        try:
            owners = reload_owners()
        except Exception:
            owners = set(OWNER_IDS)
        if uid not in owners:
            print(f"[cmd] settings DENY uid={uid} owners={sorted(owners)}", flush=True)
            return
        await message.answer("⚙️ Настройки\n\nВыберите раздел:", reply_markup=settings_root())
        return

    if cmd == "appeal":
        await message.answer(
            "📨 Апелляция принята в обработку.\n"
            "Опишите ситуацию одним сообщением — администрация рассмотрит заявку."
        )
        return


async def setup_bot_commands(bot) -> None:
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запуск бота"),
            BotCommand(command="menu", description="Главное меню"),
        ],
        scope=BotCommandScopeDefault(),
    )
    for oid in OWNER_IDS:
        try:
            await bot.set_my_commands(
                [
                    BotCommand(command="start", description="Запуск бота"),
                    BotCommand(command="menu", description="Главное меню"),
                    BotCommand(command="settings", description="Настройки бота"),
                ],
                scope=BotCommandScopeChat(chat_id=oid),
            )
        except Exception as e:
            print(f"[!] set_my_commands {oid}: {e}", flush=True)
