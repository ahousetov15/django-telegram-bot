from users.models import User
from telegram import Update
from telegram.ext import CallbackContext
from tgbot.handlers.admin import static_text
from users.models import User


def not_for_banned_users(func):
    def inner(*args, **kwargs):
        upd, cntx = args
        if isinstance(upd, Update) and isinstance(cntx, CallbackContext):
            u, created = User.get_user_and_created(upd, cntx)
            if created or (not u.is_blocked_bot):
                result = func(*args, **kwargs)
            else:
                context.bot.send_message(
                    chat_id=u.user_id,
                    text=f"Администратор ограчил ваш доступ к возможностям бота.",
                )
            return result
    return inner


def only_for_admin(func):
    def inner(*args, **kwargs):
        upd, cntx = args
        if isinstance(upd, Update) and isinstance(cntx, CallbackContext):
            if User.is_user_admin(update=upd, context=cntx):
                result = func(*args, **kwargs)
                return result
    return inner
