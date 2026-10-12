# -*- coding: utf-8 -*-
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery, Update

from config import BLACKLIST_TEXT
from storage import is_blacklisted


class BlacklistMiddleware(BaseMiddleware):
    """Блокирует всё, кроме /appeal, для пользователей из ЧС."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is None:
            return await handler(event, data)

        uid = user.id
        if not is_blacklisted(uid):
            return await handler(event, data)

        # Разрешаем только /appeal
        if isinstance(event, Message):
            text = (event.text or event.caption or "").strip().lower()
            if text.startswith("/appeal"):
                return await handler(event, data)
            await event.answer(BLACKLIST_TEXT)
            return None

        if isinstance(event, CallbackQuery):
            await event.answer("Доступ ограничен", show_alert=True)
            try:
                await event.message.answer(BLACKLIST_TEXT)
            except Exception:
                pass
            return None

        return None
