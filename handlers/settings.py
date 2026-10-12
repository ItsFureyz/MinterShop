# -*- coding: utf-8 -*-
""" /settings — только владельцы """
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import is_owner, is_admin
from keyboards import (
    settings_root, reviews_menu, bl_menu, deals_admin_menu, prem_menu, cancel_fsm,
)
from storage import (
    list_reviews, add_review, get_review, delete_review,
    list_blacklist, add_blacklist, remove_blacklist,
    deal_checks_all, delete_check, get_check,
    list_premium_users, add_premium_user, remove_premium_user,
    can_create_deal,
)

router = Router()


class SetFSM(StatesGroup):
    rev_wait_forward = State()
    rev_view_num = State()
    rev_del_num = State()
    bl_add_id = State()
    bl_del_id = State()
    deals_del_id = State()
    prem_add_id = State()
    prem_del_id = State()


def _owner_only(uid: int) -> bool:
    return is_owner(uid)


@router.message(Command("settings"))
async def cmd_settings(message: Message, state: FSMContext) -> None:
    if not _owner_only(message.from_user.id):
        return  # тихо для не-овнеров
    await state.clear()
    await message.answer(
        "⚙️ Настройки MinterShop\n\nВыберите раздел:",
        reply_markup=settings_root(),
    )


@router.callback_query(F.data == "set_close")
async def set_close(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await state.clear()
    await cb.answer()
    try:
        await cb.message.delete()
    except Exception:
        await cb.message.edit_text("Закрыто.")


@router.callback_query(F.data == "set_root")
async def set_root(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await state.clear()
    await cb.answer()
    await cb.message.edit_text(
        "⚙️ Настройки MinterShop\n\nВыберите раздел:",
        reply_markup=settings_root(),
    )


@router.callback_query(F.data == "fsm_cancel")
async def cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.answer("Отмена")
    if _owner_only(cb.from_user.id):
        await cb.message.answer("⚙️ Настройки:", reply_markup=settings_root())


# ── Reviews ──────────────────────────────────────────────────

@router.callback_query(F.data == "set_reviews")
async def set_reviews(cb: CallbackQuery) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    n = len(list_reviews())
    await cb.message.edit_text(
        f"⭐ Отзывы (сейчас {n})\n\n"
        f"Добавление: нажмите «Добавить» и перешлите боту сообщение "
        f"от клиента (с фото или без). Бот сохранит его как пересланное.",
        reply_markup=reviews_menu(),
    )


@router.callback_query(F.data == "rev_add")
async def rev_add(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.rev_wait_forward)
    await cb.answer()
    await cb.message.answer(
        "Перешлите боту сообщение-отзыв (forward from user).\n"
        "Можно с изображением.",
        reply_markup=cancel_fsm(),
    )


@router.message(SetFSM.rev_wait_forward)
async def rev_got_forward(message: Message, state: FSMContext) -> None:
    if not _owner_only(message.from_user.id):
        return
    # Должно быть пересланное сообщение
    is_fwd = bool(
        message.forward_from
        or message.forward_from_chat
        or message.forward_origin
        or message.forward_date
    )
    if not is_fwd:
        await message.answer(
            "Нужно именно переслать (forward) сообщение от человека, "
            "а не скопировать текст."
        )
        return
    # Сохраняем ссылку на сообщение в чате с ботом — при просмотре forward_message
    item = add_review(
        chat_id=message.chat.id,
        message_id=message.message_id,
        added_by=message.from_user.id,
    )
    await state.clear()
    await message.answer(
        f"✅ Отзыв №{item['id']} сохранён как пересланное сообщение.",
        reply_markup=reviews_menu(),
    )


@router.callback_query(F.data == "rev_list")
async def rev_list(cb: CallbackQuery) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    items = list_reviews()
    if not items:
        await cb.message.answer("Список отзывов пуст.")
        return
    lines = ["📋 Отзывы:"]
    for r in items:
        lines.append(f"・ №{r['id']} · msg={r['message_id']} · by={r.get('added_by')}")
    await cb.message.answer("\n".join(lines), reply_markup=reviews_menu())


@router.callback_query(F.data == "rev_view")
async def rev_view_ask(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.rev_view_num)
    await cb.answer()
    await cb.message.answer("Введите номер отзыва:", reply_markup=cancel_fsm())


@router.message(SetFSM.rev_view_num)
async def rev_view_do(message: Message, state: FSMContext, bot: Bot) -> None:
    if not _owner_only(message.from_user.id):
        return
    try:
        num = int((message.text or "").strip())
    except ValueError:
        await message.answer("Нужен номер.")
        return
    r = get_review(num)
    await state.clear()
    if not r:
        await message.answer("Нет такого номера.", reply_markup=reviews_menu())
        return
    try:
        await bot.forward_message(
            chat_id=message.chat.id,
            from_chat_id=r["chat_id"],
            message_id=r["message_id"],
        )
        await message.answer(f"↑ Отзыв №{num}", reply_markup=reviews_menu())
    except Exception as ex:
        await message.answer(
            f"Не удалось переслать отзыв №{num}: {ex}\n"
            f"(возможно сообщение удалено из чата)",
            reply_markup=reviews_menu(),
        )


@router.callback_query(F.data == "rev_del")
async def rev_del_ask(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.rev_del_num)
    await cb.answer()
    await cb.message.answer("Номер отзыва для удаления:", reply_markup=cancel_fsm())


@router.message(SetFSM.rev_del_num)
async def rev_del_do(message: Message, state: FSMContext) -> None:
    if not _owner_only(message.from_user.id):
        return
    try:
        num = int((message.text or "").strip())
    except ValueError:
        await message.answer("Нужен номер.")
        return
    await state.clear()
    ok = delete_review(num)
    await message.answer(
        "🗑 Удалено." if ok else "Не найден.",
        reply_markup=reviews_menu(),
    )


# ── Blacklist ────────────────────────────────────────────────

@router.callback_query(F.data == "set_bl")
async def set_bl(cb: CallbackQuery) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    await cb.message.edit_text(
        f"🚫 Чёрный список ({len(list_blacklist())} чел.)",
        reply_markup=bl_menu(),
    )


@router.callback_query(F.data == "bl_list")
async def bl_list(cb: CallbackQuery) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    items = list_blacklist()
    if not items:
        await cb.message.answer("ЧС пуст.")
        return
    lines = ["🚫 ЧС:"]
    for x in items:
        lines.append(f"・ <code>{x['user_id']}</code> · {x.get('reason') or '—'}")
    await cb.message.answer("\n".join(lines), reply_markup=bl_menu())


@router.callback_query(F.data == "bl_add")
async def bl_add(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.bl_add_id)
    await cb.answer()
    await cb.message.answer(
        "Пришлите user_id (число) для добавления в ЧС:",
        reply_markup=cancel_fsm(),
    )


@router.message(SetFSM.bl_add_id)
async def bl_add_do(message: Message, state: FSMContext) -> None:
    if not _owner_only(message.from_user.id):
        return
    try:
        uid = int((message.text or "").strip())
    except ValueError:
        await message.answer("Нужен числовой ID.")
        return
    await state.clear()
    ok = add_blacklist(uid, by=message.from_user.id)
    await message.answer(
        f"{'✅ Добавлен' if ok else 'Уже в ЧС'}: <code>{uid}</code>",
        reply_markup=bl_menu(),
    )


@router.callback_query(F.data == "bl_del")
async def bl_del(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.bl_del_id)
    await cb.answer()
    await cb.message.answer("user_id для удаления из ЧС:", reply_markup=cancel_fsm())


@router.message(SetFSM.bl_del_id)
async def bl_del_do(message: Message, state: FSMContext) -> None:
    if not _owner_only(message.from_user.id):
        return
    try:
        uid = int((message.text or "").strip())
    except ValueError:
        await message.answer("Нужен числовой ID.")
        return
    await state.clear()
    ok = remove_blacklist(uid)
    await message.answer(
        "🗑 Удалён." if ok else "Не был в ЧС.",
        reply_markup=bl_menu(),
    )


# ── Deal checks admin ────────────────────────────────────────

@router.callback_query(F.data == "set_deals")
async def set_deals(cb: CallbackQuery) -> None:
    if not _owner_only(cb.from_user.id) and not is_admin(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    await cb.message.edit_text(
        f"📑 Сделочные чеки ({len(deal_checks_all())})",
        reply_markup=deals_admin_menu(),
    )


@router.callback_query(F.data == "adm_deals_list")
async def adm_deals_list(cb: CallbackQuery) -> None:
    if not _owner_only(cb.from_user.id) and not is_admin(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    items = deal_checks_all()
    if not items:
        await cb.message.answer("Нет сделочных чеков.")
        return
    lines = ["📑 Сделочные чеки:"]
    for c in items[-30:]:
        lines.append(
            f"・ <code>{c['id']}</code> · {c.get('stars')}⭐ · "
            f"{c.get('status')} · creator={c.get('creator_id')}"
        )
    await cb.message.answer("\n".join(lines), reply_markup=deals_admin_menu())


@router.callback_query(F.data == "adm_deals_del")
async def adm_deals_del(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id) and not is_admin(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.deals_del_id)
    await cb.answer()
    await cb.message.answer("ID чека для удаления:", reply_markup=cancel_fsm())


@router.message(SetFSM.deals_del_id)
async def adm_deals_del_do(message: Message, state: FSMContext) -> None:
    if not _owner_only(message.from_user.id) and not is_admin(message.from_user.id):
        return
    cid = (message.text or "").strip()
    await state.clear()
    ok = delete_check(cid)
    await message.answer(
        "🗑 Удалён." if ok else "Не найден.",
        reply_markup=deals_admin_menu(),
    )


# ── Premium users ────────────────────────────────────────────

@router.callback_query(F.data == "set_prem")
async def set_prem(cb: CallbackQuery) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    await cb.message.edit_text(
        "👑 Пользователи, которым разрешено создавать сделочные чеки.\n"
        "Овнеры и админы входят автоматически.",
        reply_markup=prem_menu(),
    )


@router.callback_query(F.data == "prem_list")
async def prem_list(cb: CallbackQuery) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    items = list_premium_users()
    lines = ["👑 Премиум-пользователи бота:"]
    if not items:
        lines.append("(пусто — только овнеры/админы)")
    for x in items:
        lines.append(f"・ <code>{x['user_id']}</code>")
    await cb.message.answer("\n".join(lines), reply_markup=prem_menu())


@router.callback_query(F.data == "prem_add")
async def prem_add(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.prem_add_id)
    await cb.answer()
    await cb.message.answer("user_id для добавления:", reply_markup=cancel_fsm())


@router.message(SetFSM.prem_add_id)
async def prem_add_do(message: Message, state: FSMContext) -> None:
    if not _owner_only(message.from_user.id):
        return
    try:
        uid = int((message.text or "").strip())
    except ValueError:
        await message.answer("Нужен числовой ID.")
        return
    await state.clear()
    ok = add_premium_user(uid, by=message.from_user.id)
    await message.answer(
        f"{'✅ Добавлен' if ok else 'Уже есть'}: <code>{uid}</code>",
        reply_markup=prem_menu(),
    )


@router.callback_query(F.data == "prem_del")
async def prem_del(cb: CallbackQuery, state: FSMContext) -> None:
    if not _owner_only(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.prem_del_id)
    await cb.answer()
    await cb.message.answer("user_id для удаления:", reply_markup=cancel_fsm())


@router.message(SetFSM.prem_del_id)
async def prem_del_do(message: Message, state: FSMContext) -> None:
    if not _owner_only(message.from_user.id):
        return
    try:
        uid = int((message.text or "").strip())
    except ValueError:
        await message.answer("Нужен числовой ID.")
        return
    await state.clear()
    ok = remove_premium_user(uid)
    await message.answer(
        "🗑 Удалён." if ok else "Не найден.",
        reply_markup=prem_menu(),
    )
