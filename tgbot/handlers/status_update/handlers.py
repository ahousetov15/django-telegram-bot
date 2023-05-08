import telegram
from telegram import Update
from telegram.ext import CallbackContext
from dtb.settings import TELEGRAM_TOKEN, TELEGRAM_BOT_USERNAME
from chats.models import Chats
from users.models import User


def add_bot_to_chat(update: Update, context: CallbackContext):
    chat, created = Chats.add_chat(update=update, context=context)
    if created:
        User.notify_admins(
            update=update, 
            context=context,
            message=f"{TELEGRAM_BOT_USERNAME} был добавлен в чат {chat['chat_name']}")
    # chat_id = update.message.chat_id
    # chat_name = update.message.chat.effective_name
    # for member in update.message.new_chat_members:
    #     if member.username == TELEGRAM_BOT_USERNAME:
    #         if chat_id not in bot_chats:
    #             bot_chats[chat_id] = chat_name
    #             await context.bot.send_message(
    #                 chat_id=ADMIN_USER_ID,
    #                 text=f"{BOT_NAME} был добавлен в чат {chat_name}",
    #             )
    #             # await update.message.reply_text(f"Бот был добавлен в чат {chat_name}")


def remove_bot_from_chat(update: Update, context: CallbackContext):
    chat_id, chat_data = Chats.remove_chat(update=update, context=context)
    if chat_id:
        User.notify_admins(
            update=update, 
            context=context,
            message=f"{TELEGRAM_BOT_USERNAME} был удален из чата {chat_data['chat_name']}") 
    # chat_id = update.message.chat_id
    # chat_name = update.message.chat.effective_name
    # if update.message.left_chat_member.full_name == BOT_NAME:
    #     if chat_id in bot_chats:
    #         del bot_chats[chat_id]
    #         await context.bot.send_message(
    #             chat_id=ADMIN_USER_ID,
    #             text=f"{BOT_NAME} был удален из чата {chat_name}",
    #         )