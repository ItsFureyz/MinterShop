# -*- coding: utf-8 -*-
"""ЧС: полная тишина, кроме /appeal."""
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery

from storage import is_blacklisted


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

        # Разрешён только /appeal — без любых других ответов
        if isinstance(event, Message):
            text = (event.text or "").strip().lower()
            if text.startswith("/appeal"):
                return await handler(event, data)
            return None  # тишина

        if isinstance(event, CallbackQuery):
            # молча игнор, только закрыть «часики»
            try:
                await event.answer()
            except Exception:
                pass
            return None

        return None
