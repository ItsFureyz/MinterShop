# -*- coding: utf-8 -*-
"""Главное меню + отзывы (forward) с листанием."""
from __future__ import annotations

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from config import WELCOME_TEXT, format_money, RATE_RUB, RATE_USD, RATE_EUR
from keyboards import (
    main_menu, back_main, wallet_kb, withdraw_menu_kb, buy_check_kb, reviews_nav_kb,
)
from storage import get_user, list_reviews, checks_for_user

router = Router(name="menu")

# uid -> {fwd_id, nav_id, index}
_review_sessions: dict[int, dict] = {}


async def safe_answer(cb: CallbackQuery, text: str = "", **kwargs) -> None:
    try:
        await cb.answer(text, **kwargs)
    except Exception:
        pass


async def show(cb: CallbackQuery, text: str, kb=None) -> None:
    try:
        if cb.message.photo:
            await cb.message.edit_caption(caption=text, reply_markup=kb)
            return
        await cb.message.edit_text(text, reply_markup=kb)
        return
    except Exception:
        pass
    try:
        await cb.message.answer(text, reply_markup=kb)
    except Exception:
        pass


async def _clear_review_session(bot: Bot, uid: int) -> None:
    sess = _review_sessions.pop(uid, None)
    if not sess:
        return
    for key in ("fwd_id", "nav_id"):
        mid = sess.get(key)
        if not mid:
            continue
        try:
            await bot.delete_message(uid, mid)
        except Exception:
            pass


async def _send_review_at(bot: Bot, uid: int, index: int) -> None:
    """Удаляет прошлый forward+nav, шлёт новый forward + стрелки."""
    items = list_reviews()
    if not items:
        await bot.send_message(uid, "💬 Пока нет отзывов.", reply_markup=back_main())
        return

    index = max(0, min(index, len(items) - 1))
    r = items[index]

    await _clear_review_session(bot, uid)

    fwd_id = None
    chat_id = r.get("chat_id")
    message_id = r.get("message_id")
    if chat_id and message_id:
        try:
            fwd = await bot.forward_message(
                chat_id=uid,
                from_chat_id=int(chat_id),
                message_id=int(message_id),
            )
            fwd_id = fwd.message_id
        except Exception as e:
            err = await bot.send_message(
                uid,
                f"⚠️ Не удалось переслать отзыв №{r.get('id')}: {e.__class__.__name__}\n"
                f"Сообщение могло быть удалено из чата с ботом. Добавьте отзыв заново.",
            )
            fwd_id = err.message_id

    nav = await bot.send_message(
        uid,
        f"💬 Отзыв {index + 1} из {len(items)}",
        reply_markup=reviews_nav_kb(index, len(items)),
    )
    _review_sessions[uid] = {"fwd_id": fwd_id, "nav_id": nav.message_id, "index": index}


@router.callback_query(F.data == "back_main")
async def cb_back(cb: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await state.clear()
    await safe_answer(cb)
    await _clear_review_session(bot, cb.from_user.id)
    await show(cb, WELCOME_TEXT, main_menu())


@router.callback_query(F.data == "webwallet")
async def cb_web(cb: CallbackQuery) -> None:
    await safe_answer(cb, "Веб-кошелёк скоро будет встроен", show_alert=True)


@router.callback_query(F.data == "reviews_public")
async def cb_reviews_public(cb: CallbackQuery, bot: Bot) -> None:
    await safe_answer(cb)
    items = list_reviews()
    if not items:
        await show(cb, "💬 Пока нет отзывов.", back_main())
        return
    # короткое подтверждение в том же сообщении
    try:
        if cb.message.photo:
            await cb.message.edit_caption(
                caption=f"💬 Отзывы ({len(items)}) — листайте стрелками ↓",
                reply_markup=back_main(),
            )
        else:
            await cb.message.edit_text(
                f"💬 Отзывы ({len(items)}) — листайте стрелками ↓",
                reply_markup=back_main(),
            )
    except Exception:
        pass
    await _send_review_at(bot, cb.from_user.id, 0)


@router.callback_query(F.data.startswith("rev_pub:"))
async def cb_rev_pub_nav(cb: CallbackQuery, bot: Bot) -> None:
    await safe_answer(cb)
    try:
        index = int(cb.data.split(":")[1])
    except Exception:
        return
    await _send_review_at(bot, cb.from_user.id, index)


@router.callback_query(F.data == "noop")
async def cb_noop(cb: CallbackQuery) -> None:
    await safe_answer(cb)


@router.callback_query(F.data == "wallet")
async def cb_wallet(cb: CallbackQuery) -> None:
    await safe_answer(cb)
    u = get_user(cb.from_user.id)
    stars = float(u.get("stars", 0))
    text = (
        "👛 Кошелёк\n\n"
        f"Баланс:\n{format_money(stars)}\n\n"
        f"Курс: 1 ⭐ = {RATE_RUB} ₽ · ${RATE_USD} · €{RATE_EUR}"
    )
    await show(cb, text, wallet_kb())


@router.callback_query(F.data == "topup")
async def cb_topup(cb: CallbackQuery) -> None:
    await safe_answer(cb, "Пополнение пока недоступно", show_alert=True)


@router.callback_query(F.data == "withdraw_menu")
async def cb_wd_menu(cb: CallbackQuery) -> None:
    await safe_answer(cb)
    await show(cb, "⏬ Вывод средств\n\nВыберите способ:", withdraw_menu_kb())


@router.callback_query(F.data.in_({"wd_stars", "wd_rub", "wd_usd", "wd_eur"}))
async def cb_wd(cb: CallbackQuery) -> None:
    await safe_answer(cb, "Вывод пока недоступен", show_alert=True)


@router.callback_query(F.data == "shop")
async def cb_shop(cb: CallbackQuery) -> None:
    await safe_answer(cb, "Магазин скоро откроется", show_alert=True)


@router.callback_query(F.data == "buy_check")
async def cb_buy_check(cb: CallbackQuery) -> None:
    await safe_answer(cb)
    await show(
        cb,
        "🎫 Купить чек\n\n"
        "・ Сделочный — звёзды под условие NFT\n"
        "・ Дружеский — подарок другу",
        buy_check_kb(),
    )


@router.callback_query(F.data == "my_checks")
async def cb_my_checks(cb: CallbackQuery) -> None:
    await safe_answer(cb)
    items = checks_for_user(cb.from_user.id)
    if not items:
        await show(cb, "📋 Ваши чеки\n\nУ вас пока нет чеков.", back_main())
        return
    lines = ["📋 Ваши чеки\n"]
    for c in items:
        t = "🤝 сделочный" if c.get("type") == "deal" else "🎁 дружеский"
        lines.append(
            f"・ <code>{c['id']}</code> · {t} · {c.get('stars')} ⭐ · {c.get('status')}"
        )
    await show(cb, "\n".join(lines), back_main())
