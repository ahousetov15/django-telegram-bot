from users.models import User
from telegram import Update
from telegram.ext import CallbackContext

def not_for_banned_users(func):
    def inner(*args, **kwargs):
        upd, cntx = args
        if isinstance(upd, Update) and isinstance(cntx, CallbackContext()):
            u, created = User.get_user_and_created(upd, cntx)
            if created:
                result = func(*args, **kwargs)
            elif u.is_blocked_bot:
                context.bot.send_message(
                    chat_id=u.user_id,
                    text=f"Администратор ограчил ваш доступ к возможностям бота.",
                )
        return result
    return inner