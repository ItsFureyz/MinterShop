# -*- coding: utf-8 -*-
from aiogram import Router, F
from aiogram.types import CallbackQuery

from config import get_user, WELCOME_TEXT
from keyboards import (
    main_menu,
    withdraw_kb,
    autobuy_kb,
    wallet_kb,
    shop_kb,
    premium_kb,
    wait_kb,
    topup_kb,
)

router = Router()


async def _edit_or_answer(cb: CallbackQuery, text: str, reply_markup=None) -> None:
    """Редактирует сообщение с текстом; если было фото — шлёт новое."""
    try:
        if cb.message.photo:
            await cb.message.delete()
            await cb.message.answer(text, reply_markup=reply_markup)
        else:
            await cb.message.edit_text(text, reply_markup=reply_markup)
    except Exception:
        await cb.message.answer(text, reply_markup=reply_markup)


@router.callback_query(F.data == "topup_back")
async def cb_back_main(cb: CallbackQuery) -> None:
    await cb.answer()
    await _edit_or_answer(cb, WELCOME_TEXT, main_menu())


@router.callback_query(F.data == "withdraw")
async def cb_withdraw(cb: CallbackQuery) -> None:
    await cb.answer()
    text = (
        "❌ Нужен аккаунт Fragment от Telegram, иначе вывод не будет работать.\n"
        "Зарегистрируйтесь по кнопке ниже."
    )
    await _edit_or_answer(cb, text, withdraw_kb())


@router.callback_query(F.data == "autobuy")
async def cb_autobuy(cb: CallbackQuery) -> None:
    await cb.answer()
    u = get_user(cb.from_user.id)
    text = (
        "🤖 Автоскуп подарков\n"
        "\n"
        "Когда выйдут новинки, пришлю превью стикером и кнопки, "
        "чтобы купить в пару тапов."
    )
    await _edit_or_answer(cb, text, autobuy_kb(u["autobuy"]))


@router.callback_query(F.data == "autobuy_change")
async def cb_autobuy_change(cb: CallbackQuery) -> None:
    u = get_user(cb.from_user.id)
    u["autobuy"] = not u["autobuy"]
    await cb.answer("Включено" if u["autobuy"] else "Выключено")
    text = (
        "🤖 Автоскуп подарков\n"
        "\n"
        "Когда выйдут новинки, пришлю превью стикером и кнопки, "
        "чтобы купить в пару тапов."
    )
    await _edit_or_answer(cb, text, autobuy_kb(u["autobuy"]))


@router.callback_query(F.data == "wallet")
async def cb_wallet(cb: CallbackQuery) -> None:
    await cb.answer()
    u = get_user(cb.from_user.id)
    text = (
        "👛 Кошелёк\n"
        "\n"
        f"Звёзды: {u['stars']:g} ⭐️ · пыль: {u['dust']:g} ✨\n"
        f"Рефералка: {u['ref']:.2f}$"
    )
    await _edit_or_answer(cb, text, wallet_kb())


@router.callback_query(F.data == "shop")
async def cb_shop(cb: CallbackQuery) -> None:
    await cb.answer()
    u = get_user(cb.from_user.id)
    text = (
        "🛒 Магазин\n"
        "\n"
        f"Баланс: {u['stars']:g} ⭐️ · {u['dust']:g} ✨\n"
        f"Покупок: {u['purchases']}"
    )
    await _edit_or_answer(cb, text, shop_kb())


@router.callback_query(F.data == "premium")
async def cb_premium(cb: CallbackQuery) -> None:
    await cb.answer()
    await _edit_or_answer(cb, "💵 Выбери срок подписки:", premium_kb())


@router.callback_query(F.data == "wait_21_days")
async def cb_wait(cb: CallbackQuery) -> None:
    await cb.answer()
    text = (
        "Магазин откроется через 21 день.\n"
        "Звёзды можно вывести кнопкой ниже."
    )
    await _edit_or_answer(cb, text, wait_kb())


@router.callback_query(F.data == "gifts")
async def cb_gifts(cb: CallbackQuery) -> None:
    await cb.answer("Раздел подарков пока в разработке", show_alert=True)


@router.callback_query(F.data == "topup")
async def cb_topup(cb: CallbackQuery) -> None:
    await cb.answer()
    text = (
        "💰 Пополнение баланса\n"
        "\n"
        "Оплата пока не подключена.\n"
        "Здесь позже будут способы пополнения (CryptoBot, карта и т.д.)."
    )
    await _edit_or_answer(cb, text, topup_kb())
