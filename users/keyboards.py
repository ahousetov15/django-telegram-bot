from telegram import KeyboardButton, ReplyKeyboardMarkup


def welcome_user_keyboard():
    keyboard = [[KeyboardButton("/start")]]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    return reply_markup
