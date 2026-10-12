# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💻 Веб-кошелёк", callback_data="webwallet")],
        [InlineKeyboardButton(text="💬 Отзывы покупателей", callback_data="reviews_public")],
        [InlineKeyboardButton(text="🎫 Купить чек", callback_data="buy_check")],
        [InlineKeyboardButton(text="📋 Ваши чеки", callback_data="my_checks")],
        [InlineKeyboardButton(text="👛 Кошелёк", callback_data="wallet")],
        [InlineKeyboardButton(text="🛒 Магазин", callback_data="shop")],
    ])


def back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ])


def wallet_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💰 Пополнить", callback_data="topup")],
        [InlineKeyboardButton(text="⏬ Вывести", callback_data="withdraw_menu")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ])


def withdraw_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Звёздами (0%)", callback_data="wd_stars")],
        [InlineKeyboardButton(text="₽ Рубли", callback_data="wd_rub")],
        [InlineKeyboardButton(text="$ Доллары", callback_data="wd_usd")],
        [InlineKeyboardButton(text="€ Евро", callback_data="wd_eur")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="wallet")],
    ])


def buy_check_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🤝 Сделочный чек", callback_data="check_deal")],
        [InlineKeyboardButton(text="🎁 Дружеский чек", callback_data="check_friend")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
    ])


def deal_accept_kb(check_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔴 Отклонить", callback_data=f"deal_rej:{check_id}"),
            InlineKeyboardButton(text="🟢 Принять", callback_data=f"deal_acc:{check_id}"),
        ],
    ])


def settings_root() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Отзывы", callback_data="set_reviews")],
        [InlineKeyboardButton(text="🚫 Чёрный список", callback_data="set_bl")],
        [InlineKeyboardButton(text="📑 Сделочные чеки", callback_data="set_deals")],
        [InlineKeyboardButton(text="👑 Премиум-пользователи", callback_data="set_prem")],
        [InlineKeyboardButton(text="✖️ Закрыть", callback_data="set_close")],
    ])


def reviews_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить отзыв", callback_data="rev_add")],
        [InlineKeyboardButton(text="📋 Список отзывов", callback_data="rev_list")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="set_root")],
    ])


def reviews_list_kb(items: list) -> InlineKeyboardMarkup:
    rows = []
    for r in items:
        rows.append([InlineKeyboardButton(
            text=f"⭐ Отзыв №{r['id']}",
            callback_data=f"rev_open:{r['id']}",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="set_reviews")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def review_item_kb(num: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"rev_do_del:{num}")],
        [InlineKeyboardButton(text="⬅️ К списку", callback_data="rev_list")],
    ])


def bl_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ID", callback_data="bl_add")],
        [InlineKeyboardButton(text="📋 Список", callback_data="bl_list")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="set_root")],
    ])


def bl_list_kb(items: list) -> InlineKeyboardMarkup:
    rows = []
    for x in items:
        uid = x["user_id"]
        rows.append([InlineKeyboardButton(
            text=f"🚫 {uid}",
            callback_data=f"bl_open:{uid}",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="set_bl")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def bl_item_kb(uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Убрать из ЧС", callback_data=f"bl_do_del:{uid}")],
        [InlineKeyboardButton(text="⬅️ К списку", callback_data="bl_list")],
    ])


def deals_admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Список", callback_data="adm_deals_list")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="set_root")],
    ])


def deals_list_kb(items: list) -> InlineKeyboardMarkup:
    rows = []
    for c in items[-30:]:
        rows.append([InlineKeyboardButton(
            text=f"📑 {c['id']} · {c.get('stars')}⭐ · {c.get('status')}",
            callback_data=f"adm_deal_open:{c['id']}",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="set_deals")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def deal_admin_item_kb(cid: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"adm_deal_del:{cid}")],
        [InlineKeyboardButton(text="⬅️ К списку", callback_data="adm_deals_list")],
    ])


def prem_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить ID", callback_data="prem_add")],
        [InlineKeyboardButton(text="📋 Список", callback_data="prem_list")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="set_root")],
    ])


def prem_list_kb(items: list) -> InlineKeyboardMarkup:
    rows = []
    for x in items:
        uid = x["user_id"]
        rows.append([InlineKeyboardButton(
            text=f"👑 {uid}",
            callback_data=f"prem_open:{uid}",
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="set_prem")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def prem_item_kb(uid: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🗑 Удалить", callback_data=f"prem_do_del:{uid}")],
        [InlineKeyboardButton(text="⬅️ К списку", callback_data="prem_list")],
    ])


def cancel_fsm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✖️ Отмена", callback_data="fsm_cancel")],
    ])


def reviews_nav_kb(index: int, total: int) -> InlineKeyboardMarkup:
    """Стрелки листания отзывов. index с 0."""
    row = []
    if index > 0:
        row.append(InlineKeyboardButton(text="⬅️", callback_data=f"rev_pub:{index - 1}"))
    row.append(InlineKeyboardButton(text=f"{index + 1}/{total}", callback_data="noop"))
    if index < total - 1:
        row.append(InlineKeyboardButton(text="➡️", callback_data=f"rev_pub:{index + 1}"))
    return InlineKeyboardMarkup(inline_keyboard=[
        row,
        [InlineKeyboardButton(text="⬅️ В меню", callback_data="back_main")],
    ])


def noop_filter():
    pass
