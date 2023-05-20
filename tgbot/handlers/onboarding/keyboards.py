from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.onboarding.static_text import github_button_text, secret_level_button_text
from tgbot.states import ASK_QUESTION, QUESTION, EXPORT_QUESTIONS, SUPPORT_CHAT, END


def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    buttons = [[
        # InlineKeyboardButton(github_button_text, url="https://github.com/ohld/django-telegram-bot"),
        # InlineKeyboardButton(secret_level_button_text, callback_data=f'{SECRET_LEVEL_BUTTON}'),
        InlineKeyboardButton("Вопросы", callback_data=str(QUESTION)),
        InlineKeyboardButton("Чат поддержки", callback_data=str(SUPPORT_CHAT))
    ],
    [
        InlineKeyboardButton("Получить вопросы", callback_data=str(EXPORT_QUESTIONS)),
    ],
    [
        InlineKeyboardButton("Закончить", callback_data=str(END))
    ]
    ]

    return InlineKeyboardMarkup(buttons)
