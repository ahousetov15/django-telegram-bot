import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dtb.settings')
django.setup()

from telegram import Bot, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Updater

from dtb.settings import TELEGRAM_TOKEN, TELEGRAM_BOT_USERNAME
from tgbot.dispatcher import setup_dispatcher
from tgbot.handlers.admin.static_text import welcome_message
from users.models import User

def run_polling(tg_token: str = TELEGRAM_TOKEN):
    """ Run bot in polling mode """
    updater = Updater(tg_token, use_context=True)

    dp = updater.dispatcher
    dp = setup_dispatcher(dp)

    bot_info = Bot(tg_token).get_me()
    bot_link = f"https://t.me/{bot_info['username']}"

    print(f"Polling of '{bot_link}' has started")
    # it is really useful to send '👋' emoji to developer
    # when you run local test
    
    # update.message.reply_text("До встречи!")
    keyboard = [
        [KeyboardButton("/start")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard)
    users_id_list = User.get_users_id()
    for user_id in users_id_list:
        Bot.send_message(chat_id=user_id, text=welcome_message, reply_markup=reply_markup)
    # bot.send_message(text='👋', chat_id=<YOUR TELEGRAM ID>)

    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    run_polling()
