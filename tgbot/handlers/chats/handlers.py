from telegram import Update, InputFile
from telegram.ext import CallbackContext
from chats.models import Chats
from users.models import User
from questions.models import Question
from dtb.settings import MSK_TZ
from utils.models import datetime_str
from tgbot.handlers.utils.info import send_typing_action
from tgbot.handlers.admin import static_text
from .keyboards import keyboard_bot_chats
from .static_text import chat_exists_in_number, SUPPORT_CHAT_SET, SUPPORT_CHAT_UNSET, NO_CHATS


def list_sup_chat(update: Update, context: CallbackContext):
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


def handle_support_chat(update: Update, context: CallbackContext):
    TARGET_CHAT_ID = Chats.get_support_chat_id()
    if (
        "waiting_for_support_chat" in context.user_data
        and context.user_data["waiting_for_support_chat"]
    ):
        chat_id_selected = context.match.string[13:] # 'support_chat_-842387595'
        if chat_id_selected != str(TARGET_CHAT_ID):
            Chats.set_chat_as_support(chat_id=int(chat_id_selected))
            TARGET_CHAT_ID = Chats.get_support_chat_id()
            if chat_id_selected == str(TARGET_CHAT_ID):
                chats = Chats.chats_to_dict()
                update.callback_query.answer(
                    text=f"Чатом поддержки теперь является: '{chats[TARGET_CHAT_ID]['chat_name']}'"
                )
                update.callback_query.message.reply_text(
                    text=f"Чатом поддержки теперь является: '{chats[TARGET_CHAT_ID]['chat_name']}'"
                )
        context.user_data["waiting_for_support_chat"] = False
    #     new_question, created = Question.add_question(update=update, context=context)
    #     if created:
    #         if TARGET_CHAT_ID:
    #             context.bot.send_message(
    #                 chat_id=TARGET_CHAT_ID, text=question_formatting(update)
    #             )
    #         else:
    #             User.notify_admins(
    #                 update=update,
    #                 context=context,
    #                 message=notification_formatting(update=update),
    #             )

    #         update.message.reply_text(
    #             text="Ваш вопрос был успешно отправлен.",
    #             reply_to_message_id=update.message.message_id,
    #         )
    #     else:
    #         update.message.reply_text(
    #             text="По какой-то причине, ваш запрос не отправлен.",
    #             reply_to_message_id=update.message.message_id,
    #         )
    #     context.user_data["waiting_for_question"] = False
    # else:
    #     if TARGET_CHAT_ID:
    #         context.bot.send_message(
    #             chat_id=TARGET_CHAT_ID, text=message_formatting(update)
    #         )
    #         update.message.reply_text(
    #             text="Ваше сообщение было направленно в чат поддержки.",
    #             reply_to_message_id=update.message.message_id,
    #         )
    #     else:
    #         User.notify_admins(
    #             update=update,
    #             context=context,
    #             message=notification_formatting(update=update),
    #         )
