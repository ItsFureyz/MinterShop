# -*- coding: utf-8 -*-
"""Создание и принятие сделочных / дружеских чеков."""
from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery, Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import (
    e, DEAL_CHECK_PHOTO, is_admin, is_owner,
)
from keyboards import buy_check_kb, cancel_fsm, deal_accept_kb, back_main, main_menu
from storage import (
    create_check, get_check, update_check, can_create_deal, add_stars, get_user,
)

router = Router()


class CheckFSM(StatesGroup):
    deal_stars = State()
    deal_nft = State()
    friend_stars = State()


def _deal_forward_caption(stars: float, nft_link: str) -> str:
    return (
        f"{e('5203996991054432397', '📨')} Вам отправили сделочный чек!\n"
        f"\n"
        f"{e('5924870095925942277', '⭐')} Сумма звёзд: {stars:g}\n"
        f"{e('5870657940679039009', '🔗')} Условие: передача NFT — {nft_link}\n"
        f"\n"
        f"{e('5452069934089641166', 'ℹ️')} Что такое сделочный чек:\n"
        f"{e('5206607081334906820', '・')} Сделочный чек — это чек на звёзды, которые будут "
        f"зачислены на ваш баланс только после выполнения всех условий сделки. "
        f"Просмотреть все свои сделочные чеки можно в меню бота.\n"
        f"\n"
        f"{e('5251203410396458957', '⚠️')} Если покупатель не подтверждает получение товара, "
        f"вы можете обратиться в службу поддержки, приложив скриншоты, "
        f"подтверждающие передачу товара."
    )


@router.callback_query(F.data == "check_deal")
async def start_deal(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    user = cb.from_user
    # Telegram Premium на аккаунте
    if not getattr(user, "is_premium", False) and not is_owner(user.id) and not is_admin(user.id):
        await cb.message.answer(
            "⭐ Для создания сделочного чека нужен Telegram Premium.\n"
            "Оформите Premium и попробуйте снова."
        )
        return
    if not can_create_deal(user.id):
        await cb.message.answer(
            "⛔ Создавать сделочные чеки могут только премиум-пользователи бота "
            "(назначаются владельцем)."
        )
        return
    await state.set_state(CheckFSM.deal_stars)
    await cb.message.answer(
        "🤝 Сделочный чек\n\nВведите количество звёзд:",
        reply_markup=cancel_fsm(),
    )


@router.message(CheckFSM.deal_stars)
async def deal_stars(message: Message, state: FSMContext) -> None:
    try:
        stars = float((message.text or "").replace(",", ".").strip())
        if stars <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите число больше 0.")
        return
    await state.update_data(stars=stars)
    await state.set_state(CheckFSM.deal_nft)
    await message.answer(
        "Отправьте ссылку на NFT-подарок (например https://t.me/nft/...):",
        reply_markup=cancel_fsm(),
    )


@router.message(CheckFSM.deal_nft)
async def deal_nft(message: Message, state: FSMContext, bot: Bot) -> None:
    link = (message.text or "").strip()
    if not link.startswith("http"):
        await message.answer("Нужна ссылка, начинающаяся с http.")
        return
    data = await state.get_data()
    stars = float(data["stars"])
    await state.clear()

    check = create_check(
        creator_id=message.from_user.id,
        check_type="deal",
        stars=stars,
        nft_link=link,
    )

    await message.answer(
        f"✅ Сделочный чек <code>{check['id']}</code> создан.\n"
        f"Сумма: {stars:g} ⭐\n"
        f"NFT: {link}\n\n"
        f"Перешлите следующее сообщение продавцу:"
    )

    caption = _deal_forward_caption(stars, link)
    kb = deal_accept_kb(check["id"])
    if DEAL_CHECK_PHOTO.exists():
        await message.answer_photo(
            photo=FSInputFile(DEAL_CHECK_PHOTO),
            caption=caption,
            reply_markup=kb,
        )
    else:
        await message.answer(caption, reply_markup=kb)


@router.callback_query(F.data == "check_friend")
async def start_friend(cb: CallbackQuery, state: FSMContext) -> None:
    await cb.answer()
    await state.set_state(CheckFSM.friend_stars)
    await cb.message.answer(
        "🎁 Дружеский чек\n\nВведите количество звёзд для подарка:",
        reply_markup=cancel_fsm(),
    )


@router.message(CheckFSM.friend_stars)
async def friend_stars(message: Message, state: FSMContext) -> None:
    try:
        stars = float((message.text or "").replace(",", ".").strip())
        if stars <= 0:
            raise ValueError
    except ValueError:
        await message.answer("Введите число больше 0.")
        return
    await state.clear()
    check = create_check(
        creator_id=message.from_user.id,
        check_type="friend",
        stars=stars,
    )
    # deep-link кнопка
    me = await message.bot.get_me()
    deep = f"https://t.me/{me.username}?start=chk_{check['id']}"
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🎁 Забрать чек", url=deep)],
        ]
    )
    await message.answer(
        f"✅ Дружеский чек <code>{check['id']}</code> на {stars:g} ⭐ создан.\n"
        f"Отправьте ссылку другу:\n{deep}",
        reply_markup=kb,
    )


@router.callback_query(F.data.startswith("deal_acc:"))
async def deal_accept(cb: CallbackQuery, bot: Bot) -> None:
    check_id = cb.data.split(":", 1)[1]
    check = get_check(check_id)
    if not check:
        await cb.answer("Чек не найден", show_alert=True)
        return
    if check.get("status") != "pending":
        await cb.answer(f"Статус: {check.get('status')}", show_alert=True)
        return

    # Кнопка может быть нажата не в боте — перекидываем
    update_check(
        check_id,
        status="accepted",
        acceptor_id=cb.from_user.id,
    )
    await cb.answer("Чек принят")
    text = (
        f"🟢 Сделочный чек <code>{check_id}</code> принят.\n\n"
        f"Сумма: {check['stars']:g} ⭐\n"
        f"Условие: {check.get('nft_link')}\n\n"
        f"Ожидается подтверждение передачи NFT от покупателя.\n"
        f"Если покупатель не подтверждает передачу — обратитесь в поддержку "
        f"со скриншотами."
    )
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await bot.send_message(cb.from_user.id, text)

    # уведомить создателя
    try:
        await bot.send_message(
            check["creator_id"],
            f"🟢 Ваш сделочный чек <code>{check_id}</code> принят пользователем "
            f"id <code>{cb.from_user.id}</code>.\n"
            f"Ожидается подтверждение передачи NFT.",
        )
    except Exception:
        pass


@router.callback_query(F.data.startswith("deal_rej:"))
async def deal_reject(cb: CallbackQuery, bot: Bot) -> None:
    check_id = cb.data.split(":", 1)[1]
    check = get_check(check_id)
    if not check:
        await cb.answer("Чек не найден", show_alert=True)
        return
    if check.get("status") != "pending":
        await cb.answer(f"Статус: {check.get('status')}", show_alert=True)
        return
    update_check(check_id, status="rejected")
    await cb.answer("Чек отклонён")
    try:
        await cb.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await bot.send_message(
        cb.from_user.id,
        f"🔴 Сделочный чек <code>{check_id}</code> отклонён.",
    )
    try:
        await bot.send_message(
            check["creator_id"],
            f"🔴 Сделочный чек <code>{check_id}</code> отклонён получателем.",
        )
    except Exception:
        pass


@router.callback_query(F.data == "fsm_cancel")
async def fsm_cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.answer("Отменено")
    await cb.message.answer("Отменено.", reply_markup=main_menu())
