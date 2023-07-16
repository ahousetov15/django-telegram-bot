from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from chats.models import Chats
from .keyboards import keyboard_bot_chats
from .static_text import (
    chat_exists_in_number,
    SUPPORT_CHAT_SET,
    SUPPORT_CHAT_UNSET,
    NO_CHATS,
)

from tgbot.states import (
    SUPPORT_CHAT,
    SELECT_SUPPORT_CHAT,
    CURRENT_LEVEL,
    START_OVER,
    END,
    SELECTING_LEVEL,
    SHOWING,
)
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.main import not_for_banned_users, only_for_admin

@not_for_banned_users
@only_for_admin
def support_chat_button_press(update: Update, context: CallbackContext) -> str:
    context.user_data[CURRENT_LEVEL] = SUPPORT_CHAT
    message_text = "Бот устанавливает чаты поддержки: то куда пересылаются сообщения пользователей, для оперативной обратной связи."
    buttons = [
        [
            InlineKeyboardButton(
                text="Установить чат поддержки.", callback_data=str(SUPPORT_CHAT)
            ),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=message_text, reply_markup=keyboard)
    return SUPPORT_CHAT



@not_for_banned_users
@only_for_admin
def list_sup_chat(update: Update, context: CallbackContext):
    context.user_data[CURRENT_LEVEL] = SUPPORT_CHAT
    query = update.callback_query
    chats = Chats.chats_to_dict()
    support_chat = Chats.get_support_chat_id()
    if chats:
        text = chat_exists_in_number(str(len(chats)))
        if support_chat:
            text += SUPPORT_CHAT_SET
        else:
            text += SUPPORT_CHAT_UNSET
    else:
        text = NO_CHATS
    query.answer()
    context.user_data["waiting_for_support_chat"] = True
    # query.edit_message_text("Пожалуйста, введите ваш вопрос.")
    query.edit_message_text(text=text, reply_markup=keyboard_bot_chats(chats))
    # update.message.reply_text(text=text, reply_markup=keyboard_bot_chats(chats))
    return SELECT_SUPPORT_CHAT


@not_for_banned_users
@only_for_admin
def handle_support_chat(update: Update, context: CallbackContext):
    TARGET_CHAT_ID = Chats.get_support_chat_id()
    if (
        "waiting_for_support_chat" in context.user_data
        and context.user_data["waiting_for_support_chat"]
    ):
        chats = Chats.chats_to_dict()
        chat_id_selected = context.match.string[13:]  # 'support_chat_-842387595'
        buttons = [
            [
                InlineKeyboardButton(
                    text="Установить чат поддержки.", callback_data=str(SUPPORT_CHAT)
                ),
                InlineKeyboardButton(text="Назад.", callback_data=str(END)),
            ]
        ]
        # keyboard = InlineKeyboardMarkup.from_button(button)
        keyboard = InlineKeyboardMarkup(buttons)
        if chat_id_selected != str(TARGET_CHAT_ID):
            Chats.set_chat_as_support(chat_id=int(chat_id_selected))
            TARGET_CHAT_ID = Chats.get_support_chat_id()
            if chat_id_selected == str(TARGET_CHAT_ID):
                update.callback_query.answer(
                    text=f"Чатом поддержки теперь является: '{chats[TARGET_CHAT_ID]['chat_name']}'"
                )
                update.callback_query.message.reply_text(
                    text=f"Чатом поддержки теперь является: '{chats[TARGET_CHAT_ID]['chat_name']}'",
                    reply_markup=keyboard,
                )
        else:
            update.callback_query.message.reply_text(
                text=f"Выбран текущий чат поддержки: '{chats[TARGET_CHAT_ID]['chat_name']}'",
                reply_markup=keyboard,
            )
        context.user_data["waiting_for_support_chat"] = False

        return SUPPORT_CHAT


@not_for_banned_users
@only_for_admin
def end_support_chat(update: Update, context: CallbackContext) -> int:
    """End gathering of features and return to parent conversation."""
    user_data = context.user_data
    level = user_data[CURRENT_LEVEL]
    # Print upper level menu
    if level == SUPPORT_CHAT:
        user_data[START_OVER] = True
        onboarding_handlers.command_start(update, context)
    else:
        list_sup_chat(update, context)
    return END
