from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.onboarding.static_text import github_button_text, secret_level_button_text


def make_keyboard_for_start_command() -> InlineKeyboardMarkup:
    buttons = [[
        # InlineKeyboardButton(github_button_text, url="https://github.com/ohld/django-telegram-bot"),
        # InlineKeyboardButton(secret_level_button_text, callback_data=f'{SECRET_LEVEL_BUTTON}'),
        InlineKeyboardButton("Задать вопрос", callback_data="ask_question"),
        InlineKeyboardButton("Получить вопросы", callback_data="export_questions")
    ]]

    return InlineKeyboardMarkup(buttons)
