import datetime

from django.utils import timezone
from telegram import (
    ParseMode,
    Update,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler
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

    # Новый пользователь или уже знакомый?
    if created:
        text = static_text.start_created_ru.format(first_name=u.first_name)
    else:
        text = static_text.start_not_created_ru.format(first_name=u.first_name)
    context.user_data[CURRENT_LEVEL] = START
    # Пользователь админ?
    if u.is_admin:
        text += f"\n\n{static_text.short_describtion_for_admin_ru}"
    else:
        text += f"\n\n{static_text.short_describtion_for_user_ru}"

    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text, reply_markup=make_keyboard_for_start_command()
        )
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Начинаю работу бота.",
            reply_markup=ReplyKeyboardRemove(),
        )
        update.message.reply_text(
            text=text, reply_markup=make_keyboard_for_start_command()
        )

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


def stop_main_conv(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    # keyboard = [
    #     [KeyboardButton("/start")]
    # ]
    # reply_markup = ReplyKeyboardMarkup(keyboard)
    # context.bot.send_message(chat_id=update.effective_chat.id, text="До встречи!", reply_markup=reply_markup)
    context.user_data[CURRENT_LEVEL] = END
    context.bot.send_message(chat_id=update.effective_chat.id, text="До встречи!")
    return ConversationHandler.END


def end_buttton_clicked(update: Update, context: CallbackContext) -> int:
    """End conversation from InlineKeyboardButton."""
    # update.callback_query.answer()

    # text = "See you around!"
    # update.callback_query.edit_message_text(text=text)
    # context.bot.send_message(chat_id=update.effective_chat.id, text="/stop")
    return END


# def stop_nested(update: Update, context: CallbackContext) -> str:
#     """Completely end conversation from within nested conversation."""
#     update.message.reply_text("Okay, bye.")

#     return STOPPING


def secret_level(update: Update, context: CallbackContext) -> None:
    # callback_data: SECRET_LEVEL_BUTTON variable from manage_data.py
    """Pressed 'secret_level_button_text' after /start command"""
    user_id = extract_user_data_from_update(update)["user_id"]
    text = static_text.unlock_secret_room.format(
        user_count=User.objects.count(),
        active_24=User.objects.filter(
            updated_at__gte=timezone.now() - datetime.timedelta(hours=24)
        ).count(),
    )

    context.bot.edit_message_text(
        text=text,
        chat_id=user_id,
        message_id=update.callback_query.message.message_id,
        parse_mode=ParseMode.HTML,
    )
