# -*- coding: utf-8 -*-
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext

from config import WELCOME_TEXT, format_money, START_PHOTO, RATE_RUB, RATE_USD, RATE_EUR
from keyboards import (
    main_menu, back_main, wallet_kb, withdraw_menu_kb, buy_check_kb,
)
from storage import get_user, list_reviews, checks_for_user, get_check

router = Router()


async def _show_text(cb: CallbackQuery, text: str, kb=None) -> None:
    try:
        if cb.message.photo:
            await cb.message.delete()
            await cb.message.answer(text, reply_markup=kb)
        else:
            await cb.message.edit_text(text, reply_markup=kb)
    except Exception:
        await cb.message.answer(text, reply_markup=kb)


@router.callback_query(F.data == "back_main")
async def cb_back(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.answer()
    await _show_text(cb, WELCOME_TEXT, main_menu())


@router.callback_query(F.data == "webwallet")
async def cb_web(cb: CallbackQuery) -> None:
    await cb.answer()
    u = get_user(cb.from_user.id)
    text = (
        "💻 Веб-кошелёк\n\n"
        f"Баланс:\n{format_money(float(u.get('stars', 0)))}\n\n"
        "Полный веб-интерфейс (пополнение, вывод, транзакции) "
        "будет встроен позже."
    )
    await _show_text(cb, text, back_main())


@router.callback_query(F.data == "reviews_public")
async def cb_reviews_public(cb: CallbackQuery, bot: Bot) -> None:
    await cb.answer()
    items = list_reviews()
    if not items:
        await _show_text(cb, "💬 Пока нет отзывов.", back_main())
        return
    await _show_text(
        cb,
        f"💬 Отзывы покупателей ({len(items)} шт.)\n"
        f"Ниже — пересланные сообщения:",
        back_main(),
    )
    # Пересылаем как forwards (видно «переслано от»)
    for r in items[-10:]:  # последние 10
        try:
            await bot.forward_message(
                chat_id=cb.from_user.id,
                from_chat_id=r["chat_id"],
                message_id=r["message_id"],
            )
        except Exception:
            await cb.message.answer(
                f"⚠️ Отзыв №{r['id']} недоступен (сообщение удалено?)."
            )


@router.callback_query(F.data == "wallet")
async def cb_wallet(cb: CallbackQuery) -> None:
    await cb.answer()
    u = get_user(cb.from_user.id)
    stars = float(u.get("stars", 0))
    text = (
        "👛 Кошелёк\n\n"
        f"Баланс:\n{format_money(stars)}\n\n"
        f"Курс: 1 ⭐ = {RATE_RUB} ₽ · ${RATE_USD} · €{RATE_EUR}"
    )
    await _show_text(cb, text, wallet_kb())


@router.callback_query(F.data == "topup")
async def cb_topup(cb: CallbackQuery) -> None:
    await cb.answer()
    await _show_text(
        cb,
        "💰 Пополнение\n\nПока без функционала — скоро подключим оплату.",
        wallet_kb(),
    )


@router.callback_query(F.data == "withdraw_menu")
async def cb_wd_menu(cb: CallbackQuery) -> None:
    await cb.answer()
    await _show_text(
        cb,
        "⏬ Вывод средств\n\nВыберите способ:",
        withdraw_menu_kb(),
    )


@router.callback_query(F.data.in_({"wd_stars", "wd_rub", "wd_usd", "wd_eur"}))
async def cb_wd(cb: CallbackQuery) -> None:
    await cb.answer()
    await _show_text(
        cb,
        "⏬ Вывод пока без функционала.\n"
        "Звёзды — без комиссии; ₽/$/€ — по курсу продажи.",
        withdraw_menu_kb(),
    )


@router.callback_query(F.data == "shop")
async def cb_shop(cb: CallbackQuery) -> None:
    await cb.answer()
    await _show_text(
        cb,
        "🛒 Магазин\n\n"
        "Покупка звёзд и Telegram Premium — скоро.",
        back_main(),
    )


@router.callback_query(F.data == "buy_check")
async def cb_buy_check(cb: CallbackQuery) -> None:
    await cb.answer()
    await _show_text(
        cb,
        "🎫 Купить чек\n\n"
        "Выберите тип чека:\n"
        "・ Сделочный — звёзды под условие передачи NFT\n"
        "・ Дружеский — подарок другу",
        buy_check_kb(),
    )


@router.callback_query(F.data == "my_checks")
async def cb_my_checks(cb: CallbackQuery) -> None:
    await cb.answer()
    items = checks_for_user(cb.from_user.id)
    if not items:
        await _show_text(
            cb,
            "📋 Ваши чеки\n\nУ вас пока нет чеков.",
            back_main(),
        )
        return
    lines = ["📋 Ваши чеки\n"]
    for c in items:
        t = "🤝 сделочный" if c.get("type") == "deal" else "🎁 дружеский"
        lines.append(
            f"・ <code>{c['id']}</code> · {t} · "
            f"{c.get('stars')} ⭐ · {c.get('status')}"
        )
        if c.get("nft_link"):
            lines.append(f"  NFT: {c['nft_link']}")
    await _show_text(cb, "\n".join(lines), back_main())
