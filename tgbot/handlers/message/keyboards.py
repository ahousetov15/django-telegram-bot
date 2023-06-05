from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from tgbot.states import ASKING_QUESTION, END


def ask_question_or_no_question_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="Задать вопрос.", callback_data=str(ASKING_QUESTION)
            ),
            InlineKeyboardButton(text="Нет вопросов.", callback_data=str(END)),
        ]
    ]
    return InlineKeyboardMarkup(buttons)


def ask_question_or_back_keyboard():
    buttons = [
        [
            InlineKeyboardButton(
                text="Задать вопросы", callback_data=str(ASKING_QUESTION)
            ),
            InlineKeyboardButton(text="Назад", callback_data=str(END)),
        ]
    ]
    return InlineKeyboardMarkup(buttons)
