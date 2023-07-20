from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.onboarding.static_text import (
    github_button_text,
    secret_level_button_text,
)
from tgbot.states import ASK_QUESTION, QUESTION, EXPORT_QUESTIONS, SUPPORT_CHAT, BAN, END


def make_keyboard_for_start_command(is_admin = False) -> InlineKeyboardMarkup:
    if is_admin:
        buttons = [
            [
                InlineKeyboardButton("Вопросы", callback_data=str(QUESTION)),
                InlineKeyboardButton("Чат поддержки", callback_data=str(SUPPORT_CHAT)),
            ],
            [
                InlineKeyboardButton(
                    "Получить вопросы", callback_data=str(EXPORT_QUESTIONS)
                ),
            ],
            [
                InlineKeyboardButton(
                    "Банхаммер", callback_data=str(BAN)
                ),
            ],
            [InlineKeyboardButton("Закончить", callback_data=str(END))],
        ]
    else:
        buttons = [
                [InlineKeyboardButton("Вопросы", callback_data=str(QUESTION))],
                [InlineKeyboardButton("Закончить", callback_data=str(END))],
            ]

    return InlineKeyboardMarkup(buttons)
