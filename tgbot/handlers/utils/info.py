from functools import wraps
from typing import Dict, List, Callable

import telegram
from telegram import Update

from tgbot.main import bot


def send_typing_action(func: Callable):
    """Sends typing action while processing func command."""

    @wraps(func)
    def command_func(update, context, *args, **kwargs):
        bot.send_chat_action(
            chat_id=update.effective_message.chat_id, action=telegram.ChatAction.TYPING
        )
        return func(update, context, *args, **kwargs)

    return command_func


def extract_user_data_from_update(update: Update) -> Dict:
    """python-telegram-bot's Update instance --> User info"""
    user = update.effective_user.to_dict()

    return dict(
        user_id=user["id"],
        is_blocked_bot=False,
        **{
            k: user[k]
            for k in ["username", "first_name", "last_name", "language_code"]
            if k in user and user[k] is not None
        },
    )


def extract_new_chat_members_from_update(update: Update) -> List[Dict]:
    """Извлекаеем пользователей, только что зашедших в чат"""
    # user = update.effective_user.to_dict()
    users = update.message.new_chat_members
    users_list = []
    for user in users:
        if not user.is_bot:
            users_list.append(
                dict(
                user_id = user["id"],
                username = user["username"],
                first_name = user["first_name"],
                last_name = user["last_name"],
                language_code = user["language_code"] 
                )
            )
    # users_list = [
    #     dict(
    #         user_id=user["id"],
    #         is_blocked_bot=False,
    #         **{
    #             k: user[k]
    #             for k in ["username", "first_name", "last_name", "language_code"]
    #             if k in user and user[k] is not None
    #         },
    #     )
    #     for user in users
    # ]
    return users_list
