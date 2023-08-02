import datetime

import pprint
pp = pprint.PrettyPrinter(indent=4)


from users.models import User
from django.utils import timezone
from telegram import ParseMode, Update, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from tgbot.states import *
from tgbot.handlers.onboarding import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update
from tgbot.handlers.onboarding.keyboards import make_keyboard_for_start_command
from tgbot.handlers.main import not_for_banned_users, only_for_admin


@not_for_banned_users
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
    reply_markup_keyboard = make_keyboard_for_start_command(u.is_admin)

    # print(f"context.user_data : {pp.pformat(context.user_data)}")
    # if context.user_data.get(START_OVER):
    #     update.callback_query.answer()
    #     update.callback_query.edit_message_text(text=text, reply_markup=reply_markup_keyboard)
    # else:
    context.bot.send_message(
        # chat_id=update.effective_chat.id,
        chat_id=u.user_id,
        text="Начинаю работу бота.",
        reply_markup=ReplyKeyboardRemove(),
    )
    
    # update.message.reply_text(text=text, reply_markup=reply_markup_keyboard)
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text,
        reply_markup=reply_markup_keyboard,
    )
    context.user_data[START_OVER] = False
    return SELECTING_ACTION



@not_for_banned_users
def stop_main_conv(update: Update, context: CallbackContext) -> int:
    """End Conversation by command."""
    context.user_data[CURRENT_LEVEL] = END
    context.bot.send_message(chat_id=update.effective_chat.id, text="До встречи!")
    return ConversationHandler.END


@not_for_banned_users
def end_buttton_clicked(update: Update, context: CallbackContext) -> str:
    """End conversation from InlineKeyboardButton."""
    return END


@not_for_banned_users
@only_for_admin
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
