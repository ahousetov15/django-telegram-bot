from datetime import timedelta

from django.utils.timezone import now
from telegram import ParseMode, Update
from telegram.ext import CallbackContext
from tgbot.handlers.admin import static_text
from tgbot.handlers.admin.utils import _get_csv_from_qs_values
from tgbot.handlers.utils.info import send_typing_action
from tgbot.handlers.main import not_for_banned_users
from users.models import User


@not_for_banned_users
def admin(update: Update, context: CallbackContext) -> None:
    """Show help info about all secret admins commands"""
    u = User.get_user(update, context)
    if not u.is_admin:
        context.bot.send_message(
            chat_id=u.user_id,
            text=static_text.only_for_admins_ru,
        )
        return
    update.message.reply_text(static_text.secret_admin_commands)


@not_for_banned_users
def stats(update: Update, context: CallbackContext) -> None:
    """Show help info about all secret admins commands"""
    u = User.get_user(update, context)
    if not u.is_admin:
        update.message.reply_text(static_text.only_for_admins)
        return

    text = static_text.users_amount_stat.format(
        user_count=User.objects.count(),  # count may be ineffective if there are a lot of users.
        active_24=User.objects.filter(
            updated_at__gte=now() - timedelta(hours=24)
        ).count(),
    )

    update.message.reply_text(
        text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


# @send_typing_action
@not_for_banned_users
def export_users(update: Update, context: CallbackContext) -> None:
    u = User.get_user(update, context)
    if not u.is_admin:
        if update:
            message_attr = getattr(update, 'message')
            if message_attr:
                update.message.reply_text(static_text.only_for_admins)
            else:
                context.bot.send_message(
                    chat_id=u.user_id,
                    text=static_text.only_for_admins_ru,
                )       
        else:
            context.bot.send_message(
                chat_id=u.user_id,
                text=static_text.only_for_admins_ru,
            )   
        return

    # in values argument you can specify which fields should be returned in output csv
    users = User.objects.all().values()
    csv_users = _get_csv_from_qs_values(users)
    context.bot.send_document(chat_id=u.user_id, document=csv_users)
