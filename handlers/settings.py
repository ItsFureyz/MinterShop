# -*- coding: utf-8 -*-
"""/settings — только владельцы. Списки = инлайн-кнопки."""
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import is_owner, is_admin, OWNER_IDS, reload_owners
from keyboards import (
    settings_root, reviews_menu, reviews_list_kb, review_item_kb,
    bl_menu, bl_list_kb, bl_item_kb,
    deals_admin_menu, deals_list_kb, deal_admin_item_kb,
    prem_menu, prem_list_kb, prem_item_kb,
    cancel_fsm,
)
from storage import (
    list_reviews, add_review_content, get_review, delete_review,
    list_blacklist, add_blacklist, remove_blacklist,
    deal_checks_all, delete_check, get_check,
    list_premium_users, add_premium_user, remove_premium_user,
)

router = Router()


class SetFSM(StatesGroup):
    rev_wait_forward = State()
    bl_add_id = State()
    prem_add_id = State()


def _own(uid: int) -> bool:
    reload_owners()
    return is_owner(uid)



@router.callback_query(F.data == "set_close")
async def set_close(cb: CallbackQuery, state: FSMContext) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await state.clear()
    await cb.answer()
    try:
        await cb.message.delete()
    except Exception:
        pass


@router.callback_query(F.data == "set_root")
async def set_root(cb: CallbackQuery, state: FSMContext) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await state.clear()
    await cb.answer()
    await cb.message.edit_text("⚙️ Настройки\n\nВыберите раздел:", reply_markup=settings_root())


@router.callback_query(F.data == "fsm_cancel")
async def cancel(cb: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await cb.answer("Отмена")
    if _own(cb.from_user.id):
        try:
            await cb.message.edit_text("⚙️ Настройки:", reply_markup=settings_root())
        except Exception:
            await cb.message.answer("⚙️ Настройки:", reply_markup=settings_root())


# ── Reviews ──────────────────────────────────────────────────

@router.callback_query(F.data == "set_reviews")
async def set_reviews(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    n = len(list_reviews())
    await cb.message.edit_text(
        f"⭐ Отзывы ({n})\n\n"
        f"«Добавить» → перешлите боту сообщение от клиента (forward).",
        reply_markup=reviews_menu(),
    )


@router.callback_query(F.data == "rev_add")
async def rev_add(cb: CallbackQuery, state: FSMContext) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.rev_wait_forward)
    await cb.answer()
    await cb.message.answer(
        "Перешлите боту сообщение-отзыв (именно forward от человека).\n⚠️ Не удаляйте это сообщение из чата с ботом — иначе пересылка сломается.",
        reply_markup=cancel_fsm(),
    )


@router.message(SetFSM.rev_wait_forward)
async def rev_got(message: Message, state: FSMContext) -> None:
    if not _own(message.from_user.id):
        return
    is_fwd = bool(
        message.forward_from
        or message.forward_from_chat
        or message.forward_origin
        or message.forward_date
    )
    if not is_fwd:
        await message.answer("Нужен forward, не копия текста.")
        return

    # Имя автора отзыва
    from_name = ""
    from_username = ""
    if message.forward_from:
        from_name = message.forward_from.full_name or ""
        from_username = message.forward_from.username or ""
    elif message.forward_origin is not None:
        origin = message.forward_origin
        sender = getattr(origin, "sender_user", None)
        if sender is not None:
            from_name = getattr(sender, "full_name", "") or ""
            from_username = getattr(sender, "username", "") or ""
        else:
            from_name = getattr(origin, "sender_user_name", "") or ""
            chat = getattr(origin, "sender_chat", None)
            if chat is not None:
                from_name = getattr(chat, "title", "") or from_name

    photo_id = ""
    if message.photo:
        photo_id = message.photo[-1].file_id

    text_body = (message.text or "").strip()
    caption = (message.caption or "").strip()

    item = add_review_content(
        text=text_body,
        caption=caption,
        photo_id=photo_id,
        from_name=from_name,
        from_username=from_username,
        chat_id=message.chat.id,
        message_id=message.message_id,
        added_by=message.from_user.id,
    )
    await state.clear()
    await message.answer(
        f"✅ Отзыв №{item['id']} сохранён (будет пересылаться как forward)"
        + (f" от {from_name}" if from_name else "")
        + ".",
        reply_markup=reviews_menu(),
    )


@router.callback_query(F.data == "rev_list")
async def rev_list(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    items = list_reviews()
    if not items:
        await cb.message.edit_text("Список отзывов пуст.", reply_markup=reviews_menu())
        return
    await cb.message.edit_text(
        "📋 Выберите отзыв:",
        reply_markup=reviews_list_kb(items),
    )


@router.callback_query(F.data.startswith("rev_open:"))
async def rev_open(cb: CallbackQuery, bot: Bot) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    num = int(cb.data.split(":")[1])
    r = get_review(num)
    if not r:
        await cb.answer("Не найден", show_alert=True)
        return
    await cb.answer()
    ok = False
    if r.get("chat_id") and r.get("message_id"):
        try:
            await bot.forward_message(
                cb.from_user.id, int(r["chat_id"]), int(r["message_id"])
            )
            ok = True
        except Exception as e:
            await cb.message.answer(f"⚠️ Forward не удался: {e}")
    if not ok:
        await cb.message.answer(
            f"Отзыв №{num} недоступен для пересылки. "
            f"Добавьте заново и не удаляйте сообщение из чата с ботом."
        )
    await cb.message.answer(f"Отзыв №{num}", reply_markup=review_item_kb(num))


@router.callback_query(F.data.startswith("rev_do_del:"))
async def rev_do_del(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    num = int(cb.data.split(":")[1])
    ok = delete_review(num)
    await cb.answer("Удалено" if ok else "Не найден", show_alert=True)
    items = list_reviews()
    if items:
        await cb.message.edit_text("📋 Выберите отзыв:", reply_markup=reviews_list_kb(items))
    else:
        await cb.message.edit_text("Список отзывов пуст.", reply_markup=reviews_menu())


# ── Blacklist ────────────────────────────────────────────────

@router.callback_query(F.data == "set_bl")
async def set_bl(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    await cb.message.edit_text(
        f"🚫 Чёрный список ({len(list_blacklist())})",
        reply_markup=bl_menu(),
    )


@router.callback_query(F.data == "bl_list")
async def bl_list(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    items = list_blacklist()
    if not items:
        await cb.message.edit_text("ЧС пуст.", reply_markup=bl_menu())
        return
    await cb.message.edit_text("🚫 Выберите запись:", reply_markup=bl_list_kb(items))


@router.callback_query(F.data.startswith("bl_open:"))
async def bl_open(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    uid = int(cb.data.split(":")[1])
    await cb.answer()
    await cb.message.edit_text(
        f"🚫 Пользователь <code>{uid}</code>",
        reply_markup=bl_item_kb(uid),
    )


@router.callback_query(F.data.startswith("bl_do_del:"))
async def bl_do_del(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    uid = int(cb.data.split(":")[1])
    ok = remove_blacklist(uid)
    await cb.answer("Убран" if ok else "Не был в ЧС", show_alert=True)
    items = list_blacklist()
    if items:
        await cb.message.edit_text("🚫 Выберите запись:", reply_markup=bl_list_kb(items))
    else:
        await cb.message.edit_text("ЧС пуст.", reply_markup=bl_menu())


@router.callback_query(F.data == "bl_add")
async def bl_add(cb: CallbackQuery, state: FSMContext) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.bl_add_id)
    await cb.answer()
    await cb.message.answer("Пришлите user_id:", reply_markup=cancel_fsm())


@router.message(SetFSM.bl_add_id)
async def bl_add_do(message: Message, state: FSMContext) -> None:
    if not _own(message.from_user.id):
        return
    try:
        uid = int((message.text or "").strip())
    except ValueError:
        await message.answer("Нужен числовой ID.")
        return
    await state.clear()
    ok = add_blacklist(uid, by=message.from_user.id)
    await message.answer(
        f"{'✅ В ЧС' if ok else 'Уже в ЧС'}: <code>{uid}</code>",
        reply_markup=bl_menu(),
    )


# ── Deals admin ──────────────────────────────────────────────

@router.callback_query(F.data == "set_deals")
async def set_deals(cb: CallbackQuery) -> None:
    if not (_own(cb.from_user.id) or is_admin(cb.from_user.id)):
        await cb.answer()
        return
    await cb.answer()
    await cb.message.edit_text(
        f"📑 Сделочные чеки ({len(deal_checks_all())})",
        reply_markup=deals_admin_menu(),
    )


@router.callback_query(F.data == "adm_deals_list")
async def adm_deals_list(cb: CallbackQuery) -> None:
    if not (_own(cb.from_user.id) or is_admin(cb.from_user.id)):
        await cb.answer()
        return
    await cb.answer()
    items = deal_checks_all()
    if not items:
        await cb.message.edit_text("Нет чеков.", reply_markup=deals_admin_menu())
        return
    await cb.message.edit_text("📑 Выберите чек:", reply_markup=deals_list_kb(items))


@router.callback_query(F.data.startswith("adm_deal_open:"))
async def adm_deal_open(cb: CallbackQuery) -> None:
    if not (_own(cb.from_user.id) or is_admin(cb.from_user.id)):
        await cb.answer()
        return
    cid = cb.data.split(":", 1)[1]
    c = get_check(cid)
    if not c:
        await cb.answer("Не найден", show_alert=True)
        return
    await cb.answer()
    text = (
        f"📑 Чек <code>{c['id']}</code>\n"
        f"Тип: {c.get('type')}\n"
        f"Сумма: {c.get('stars')} ⭐\n"
        f"Статус: {c.get('status')}\n"
        f"Создатель: <code>{c.get('creator_id')}</code>\n"
        f"NFT: {c.get('nft_link') or '—'}"
    )
    await cb.message.edit_text(text, reply_markup=deal_admin_item_kb(cid))


@router.callback_query(F.data.startswith("adm_deal_del:"))
async def adm_deal_del(cb: CallbackQuery) -> None:
    if not (_own(cb.from_user.id) or is_admin(cb.from_user.id)):
        await cb.answer()
        return
    cid = cb.data.split(":", 1)[1]
    ok = delete_check(cid)
    await cb.answer("Удалён" if ok else "Не найден", show_alert=True)
    items = deal_checks_all()
    if items:
        await cb.message.edit_text("📑 Выберите чек:", reply_markup=deals_list_kb(items))
    else:
        await cb.message.edit_text("Нет чеков.", reply_markup=deals_admin_menu())


# ── Premium users ────────────────────────────────────────────

@router.callback_query(F.data == "set_prem")
async def set_prem(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    await cb.message.edit_text(
        "👑 Кто может создавать сделочные чеки\n(овнеры/админы — всегда)",
        reply_markup=prem_menu(),
    )


@router.callback_query(F.data == "prem_list")
async def prem_list(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await cb.answer()
    items = list_premium_users()
    if not items:
        await cb.message.edit_text("Список пуст.", reply_markup=prem_menu())
        return
    await cb.message.edit_text("👑 Выберите:", reply_markup=prem_list_kb(items))


@router.callback_query(F.data.startswith("prem_open:"))
async def prem_open(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    uid = int(cb.data.split(":")[1])
    await cb.answer()
    await cb.message.edit_text(
        f"👑 <code>{uid}</code>",
        reply_markup=prem_item_kb(uid),
    )


@router.callback_query(F.data.startswith("prem_do_del:"))
async def prem_do_del(cb: CallbackQuery) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    uid = int(cb.data.split(":")[1])
    ok = remove_premium_user(uid)
    await cb.answer("Удалён" if ok else "Не найден", show_alert=True)
    items = list_premium_users()
    if items:
        await cb.message.edit_text("👑 Выберите:", reply_markup=prem_list_kb(items))
    else:
        await cb.message.edit_text("Список пуст.", reply_markup=prem_menu())


@router.callback_query(F.data == "prem_add")
async def prem_add(cb: CallbackQuery, state: FSMContext) -> None:
    if not _own(cb.from_user.id):
        await cb.answer()
        return
    await state.set_state(SetFSM.prem_add_id)
    await cb.answer()
    await cb.message.answer("user_id:", reply_markup=cancel_fsm())


@router.message(SetFSM.prem_add_id)
async def prem_add_do(message: Message, state: FSMContext) -> None:
    if not _own(message.from_user.id):
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
