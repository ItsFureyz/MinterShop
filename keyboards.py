# -*- coding: utf-8 -*-
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💻 Веб-Кошелек", callback_data="webwallet")],
            [InlineKeyboardButton(text="💫 Вывести звезды", callback_data="withdraw")],
            [InlineKeyboardButton(text="🤖 Автоскупщик подарков", callback_data="autobuy")],
            [
                InlineKeyboardButton(text="👛 Кошелек", callback_data="wallet"),
                InlineKeyboardButton(text="🛒 Магазин", callback_data="shop"),
            ],
            [InlineKeyboardButton(text="💰 Пополнить Баланс", callback_data="topup")],
            [InlineKeyboardButton(text="🌟 Создать чек", switch_inline_query="check ")],
        ]
    )


def withdraw_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🏴‍☠️ Зарегистрироваться", callback_data="fragment_reg")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="topup_back")],
        ]
    )


def autobuy_kb(enabled: bool) -> InlineKeyboardMarkup:
    mark = "✅" if enabled else "❎"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"Авто-скупщик: {mark}",
                callback_data="autobuy_change",
            )],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="topup_back")],
        ]
    )


def wallet_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💰 Пополнить", callback_data="topup")],
            [InlineKeyboardButton(text="⏬️ Вывести звёзды", callback_data="withdraw")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="topup_back")],
        ]
    )


def shop_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="💫 Премиум", callback_data="premium"),
                InlineKeyboardButton(text="🌟 Подарки", callback_data="gifts"),
            ],
            [InlineKeyboardButton(text="💰 Пополнить", callback_data="topup")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="topup_back")],
        ]
    )


def premium_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="3 месяца", callback_data="wait_21_days")],
            [InlineKeyboardButton(text="6 месяца", callback_data="wait_21_days")],
            [InlineKeyboardButton(text="12 месяцев", callback_data="wait_21_days")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="shop")],
        ]
    )


def wait_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⏬️ Вывести звёзды", callback_data="withdraw")],
        ]
    )


def topup_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="topup_back")],
        ]
    )


def back_main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="topup_back")],
        ]
    )
