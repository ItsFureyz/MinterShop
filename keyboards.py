# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💻 Веб-кошелёк", callback_data="webwallet")],
            [InlineKeyboardButton(text="💬 Отзывы покупателей", callback_data="reviews_public")],
            [InlineKeyboardButton(text="🎫 Купить чек", callback_data="buy_check")],
            [InlineKeyboardButton(text="📋 Ваши чеки", callback_data="my_checks")],
            [InlineKeyboardButton(text="👛 Кошелёк", callback_data="wallet")],
            [InlineKeyboardButton(text="🛒 Магазин", callback_data="shop")],
        ]
    )


def back_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
        ]
    )


def wallet_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 Пополнить", callback_data="topup")],
            [InlineKeyboardButton(text="⏬ Вывести", callback_data="withdraw_menu")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
        ]
    )


def withdraw_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Вывести звёздами (0% комиссия)", callback_data="wd_stars")],
            [InlineKeyboardButton(text="₽ В рублях", callback_data="wd_rub")],
            [InlineKeyboardButton(text="$ В долларах", callback_data="wd_usd")],
            [InlineKeyboardButton(text="€ В евро", callback_data="wd_eur")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="wallet")],
        ]
    )


def buy_check_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🤝 Сделочный чек", callback_data="check_deal")],
            [InlineKeyboardButton(text="🎁 Дружеский чек", callback_data="check_friend")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")],
        ]
    )


def deal_accept_kb(check_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🔴 Отклонить", callback_data=f"deal_rej:{check_id}"),
                InlineKeyboardButton(text="🟢 Принять", callback_data=f"deal_acc:{check_id}"),
            ],
        ]
    )


# ── Settings ─────────────────────────────────────────────────

def settings_root() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐ Отзывы", callback_data="set_reviews")],
            [InlineKeyboardButton(text="🚫 Чёрный список", callback_data="set_bl")],
            [InlineKeyboardButton(text="📑 Сделочные чеки", callback_data="set_deals")],
            [InlineKeyboardButton(text="👑 Премиум-пользователи", callback_data="set_prem")],
            [InlineKeyboardButton(text="✖️ Закрыть", callback_data="set_close")],
        ]
    )


def reviews_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить", callback_data="rev_add")],
            [InlineKeyboardButton(text="📋 Список", callback_data="rev_list")],
            [InlineKeyboardButton(text="🔍 Смотреть №", callback_data="rev_view")],
            [InlineKeyboardButton(text="🗑 Удалить №", callback_data="rev_del")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="set_root")],
        ]
    )


def bl_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить ID", callback_data="bl_add")],
            [InlineKeyboardButton(text="📋 Список", callback_data="bl_list")],
            [InlineKeyboardButton(text="🗑 Удалить ID", callback_data="bl_del")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="set_root")],
        ]
    )


def deals_admin_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📋 Список", callback_data="adm_deals_list")],
            [InlineKeyboardButton(text="🗑 Удалить ID", callback_data="adm_deals_del")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="set_root")],
        ]
    )


def prem_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить ID", callback_data="prem_add")],
            [InlineKeyboardButton(text="📋 Список", callback_data="prem_list")],
            [InlineKeyboardButton(text="🗑 Удалить ID", callback_data="prem_del")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="set_root")],
        ]
    )


def cancel_fsm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✖️ Отмена", callback_data="fsm_cancel")],
        ]
    )
