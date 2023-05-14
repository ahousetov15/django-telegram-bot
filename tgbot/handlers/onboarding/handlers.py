import datetime

from django.utils import timezone
from telegram import ParseMode, Update
from telegram.ext import CallbackContext, ContextTypes
from tgbot.states import *
from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from users.models import User
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command


# def command_start(update: Update, context: CallbackContext) -> None:
#     u, created = User.get_user_and_created(update, context)

#     if created:
#         text = static_text.start_created_ru.format(first_name=u.first_name)
#     else:
#         text = static_text.start_not_created_ru.format(first_name=u.first_name)

#     update.message.reply_text(text=text,
#                               reply_markup=make_keyboard_for_start_command())


def command_start(update: Update, context: CallbackContext) -> None:
    u, created = User.get_user_and_created(update, context)

    if created:
        text = static_text.start_created_ru.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created_ru.format(first_name=u.first_name)
    
        

    update.message.reply_text(text=text,
                              reply_markup=make_keyboard_for_start_command())
    
    return SELECTING_ACTION


def stop(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    update.message.reply_text("Okay, bye.")

    return END


def end(update: Update, context: CallbackContext) -> int:
    """End conversation from InlineKeyboardButton."""
    update.callback_query.answer()

    text = "See you around!"
    update.callback_query.edit_message_text(text=text)

    return END


def stop_nested(update: Update, context: CallbackContext) -> str:
    """Completely end conversation from within nested conversation."""
    update.message.reply_text("Okay, bye.")

    return STOPPING





def secret_level(update: Update, context: CallbackContext) -> None:
    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """ Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)['user_id']
    text = static_text.unlock_secret_room.format(
        user_count=User.objects.count(),
        active_24=User.objects.filter(updated_at__gte=timezone.now() - datetime.timedelta(hours=24)).count()
    )

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML
    )