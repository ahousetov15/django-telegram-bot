import telegram
from telegram import Update
from telegram.ext import CallbackContext
from dtb.settings import TELEGRAM_TOKEN, TELEGRAM_BOT_USERNAME
from chats.models import Chats
from users.models import User
from tgbot.handlers.main import not_for_banned_users

@not_for_banned_users
def add_bot_to_chat(update: Update, context: CallbackContext):
    chat, created = Chats.add_chat(update=update, context=context)
    if created:
        User.notify_admins(
            update=update,
            context=context,
            message=f"{TELEGRAM_BOT_USERNAME} был добавлен в чат {chat['chat_name']}",
        )


@not_for_banned_users
def remove_bot_from_chat(update: Update, context: CallbackContext):
    chat_id, chat_data = Chats.remove_chat(update=update, context=context)
    if chat_id:
        User.notify_admins(
            update=update,
            context=context,
            message=f"{TELEGRAM_BOT_USERNAME} был удален из чата {chat_data['chat_name']}",
        )
