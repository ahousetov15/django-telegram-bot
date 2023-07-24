from telegram import Update, InputFile, error
from telegram.ext import CallbackContext
from chats.models import Chats, User
from questions.models import Question
from dtb.settings import MSK_TZ
from utils.models import datetime_str
from tgbot.handlers.admin import static_text
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.buttons import not_in_conv_buttons
from tgbot.handlers.main import not_for_banned_users
from dtb.settings import ADMINS_BY_DEFAULT
from tgbot.states import (
    ASK_QUESTION,
    ASKING_QUESTION,
    HAS_QUESTION,
    QUESTION,
    START_OVER,
    TYPING,
    END,
    CURRENT_LEVEL,
    STATES_NO_CHAT_SUPPORT,
    START_COMMAND,
    STOP_COMMAND
)
from .keyboards import (
    ask_question_or_no_question_keyboard,
    ask_question_or_back_keyboard,
)


@not_for_banned_users
def ask_question_button_press(update: Update, context: CallbackContext) -> str:
    context.user_data[CURRENT_LEVEL] = QUESTION
    message_text = "Вы можете задать вопросы ведущему. Они будут сохранены и вы получите ответ, когда ведущий освободиться."
    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=message_text, reply_markup=ask_question_or_back_keyboard()
    )
    return ASKING_QUESTION


# def ask_question(update: Update, context: CallbackContext) -> str:
#     """Select a feature to update for the person."""
#     buttons = [
#         [
#             InlineKeyboardButton(text="Задать вопрос.", callback_data=str(ASKING_QUESTION)),
#             InlineKeyboardButton(text="Нет вопросов.", callback_data=str(END)),
#         ]
#     ]
#     keyboard = InlineKeyboardMarkup(buttons)

#     # If we collect features for a new person, clear the cache and save the gender
#     if not context.user_data.get(START_OVER):
#         # context.user_data[FEATURES] = {GENDER: update.callback_query.data}
#         # text = "У вас есть вопрос?"

#         # update.callback_query.answer()
#         # update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
#         return asking_question(update, context)
#     # But after we do that, we need to send a new message
#     else:
#         text = "Отлично! Остались вопросы?"
#         update.message.reply_text(text=text, reply_markup=keyboard)


#     context.user_data[START_OVER] = False
#     return ASKING_QUESTION


@not_for_banned_users
def asking_question(update: Update, context: CallbackContext) -> str:
    """Prompt user to input data for selected feature."""
    # context.user_data[CURRENT_FEATURE] = update.callback_query.data
    query = update.callback_query
    query.answer()
    context.user_data["waiting_for_question"] = True
    text = "Пожалуйста, введите ваш вопрос."

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)

    return TYPING


@not_for_banned_users
def export_questions(update: Update, context: CallbackContext):
    (
        file_name,
        excel_questions,
        count,
        first_date,
        last_date,
    ) = Question.export_question_to_excel()
    u = User.get_user(update, context)
    if not u.is_admin:
        context.bot.send_message(
            chat_id=u.user_id,
            text=static_text.only_for_admins_ru,
        )
        # update.message.reply_text(static_text.only_for_admins_ru)
        return
    if excel_questions:
        with excel_questions as file:
            caption = f"Всего вопросов: {count}\nДата первого вопроса: {first_date}\nДата последнего вопроса: {last_date}\n\n"
            context.bot.send_document(
                chat_id=u.user_id,
                document=InputFile(file, filename=file_name),
                caption=caption,
            )
        if u.user_id in ADMINS_BY_DEFAULT:
            """
            Удаляю вопросы из таблицы, только если их скачали администраторы по умолчанию
            """
            removed = Question.remove_question()
    else:
        context.bot.send_message(chat_id=u.user_id, text=file_name)


def question_formatting(update: Update):
    result = f"#вопрос\n"
    result += f"от пользователя: {update.message.from_user.full_name}\n"
    result += f"логин: {update.message.from_user.name}\n"
    result += f"задан: {datetime_str(update.message.date)} по Москве"
    result += f"\n\n{update.message.text}"
    return result


def message_formatting(update: Update):
    result = f"#сообщение\n"
    result += f"от пользователя: {update.message.from_user.full_name}\n"
    result += f"логин: {update.message.from_user.name}\n"
    result += f"отправлено в {update.message.date.astimezone(MSK_TZ).strftime('%Y-%m-%d %H:%M:%S')} по Москве"
    result += f"\n\n{update.message.text}"
    return result


def notification_formatting(update: Update):
    result = f"#уведомление администратору\n\n"
    result = f"получено сообщение или вопрос от пользователя, но чат поддержки не указан ИЛИ указан неверно. Пожалуйста, укажите чат поддержки или все сообщения будут пересылаться сюда.\n\n"
    result += f"от пользователя: {update.message.from_user.full_name}\n"
    result += f"логин: {update.message.from_user.name}\n"
    result += f"отправлено в {update.message.date.astimezone(MSK_TZ).strftime('%Y-%m-%d %H:%M:%S')} по Москве"
    result += f"\n\n{update.message.text}"
    return result


@not_for_banned_users
def handle_only_questions(update: Update, context: CallbackContext) -> str:
    TARGET_CHAT_ID = Chats.get_support_chat_id()
    if (
        "waiting_for_question" in context.user_data
        and context.user_data["waiting_for_question"]
    ):
        new_question, created = Question.add_question(update=update, context=context)
        if created:
            if TARGET_CHAT_ID:
                print(f"tgbot/handlers/message/handlers.py: context : {context}")
                print(f"tgbot/handlers/message/handlers.py: TARGET_CHAT_ID : {TARGET_CHAT_ID}")
                print(f"tgbot/handlers/message/handlers.py: update : {update}")
                try:
                    context.bot.send_message(
                        chat_id=TARGET_CHAT_ID, text=question_formatting(update)
                    )
                except error.BadRequest as Br:
                    print(f"Плохой запрос на отправку: {Br}")
                    User.notify_admins(
                        update=update,
                        context=context,
                        message=notification_formatting(update=update),
                    )
            else:
                User.notify_admins(
                    update=update,
                    context=context,
                    message=notification_formatting(update=update),
                )

            context.user_data[START_OVER] = True
            text = "Ваш вопрос был успешно отправлен. У вас остались вопросы?"
        else:
            text = "По какой-то причине, ваш запрос не отправлен."

        # update.message.reply_text(
        #     text=text,
        #     reply_to_message_id=update.message.message_id,
        #     reply_markup=ask_question_or_no_question_keyboard(),
        # )
        context.bot.send_message(
            chat_id=TARGET_CHAT_ID, 
            reply_to_message_id=update.message.message_id, 
            text=question_formatting(update)
        )
        context.user_data["waiting_for_question"] = False
    return ASKING_QUESTION




@not_for_banned_users
def handle_message_or_question(update: Update, context: CallbackContext):
    TARGET_CHAT_ID = Chats.get_support_chat_id()
    if ("waiting_for_question" in context.user_data and context.user_data["waiting_for_question"]):
        return handle_only_questions(update, context)
    else:
        cur_lvl = context.user_data.get("CURRENT_LEVEL")
        msg_text = update.message
        is_start_cmd, is_stop_cmd = None, None 
        if msg_text:
            msg_text = msg_text.text 
            is_start_cmd = msg_text == START_COMMAND
            is_stop_cmd = msg_text == STOP_COMMAND
        
         
        if is_start_cmd ^ is_stop_cmd: 
            """
            Если пришла команда то отрабатываю ее вне зависимости от того
            в каком состоянии находится бот. Исхожу из того, что есть обработка команды дошла до сюда, 
            то уже надо рубить с плеча
            """ 
            if is_start_cmd:
                onboarding_handlers.command_start(update, context)
            else:
                onboarding_handlers.stop_main_conv(update, context)
        elif not cur_lvl or cur_lvl == END:
            """
            Здесь случай, когда никакого уровня(стейта) нет. Значит беседа не начата вообще или уже окончена. 
            Уведомляем пользователя, что хорошо бы перезапустить.
            """ 
            not_in_conv_buttons.handle_button_press(update, context)
        elif cur_lvl == QUESTION:
                context.bot.send_message(
                    text="Нажмите 'Задать вопрос' чтобы задать вопрос ведущему или 'Назад' чтобы вернуться в основное меню.",
                    reply_to_message_id=update.message.message_id,
                    reply_markup=ask_question_or_back_keyboard(),
                )      
                # update.message.reply_text(
                #     text="Нажмите 'Задать вопрос' чтобы задать вопрос ведущему или 'Назад' чтобы вернуться в основное меню.",
                #     reply_to_message_id=update.message.message_id,
                #     reply_markup=ask_question_or_back_keyboard(),
                # )
        elif cur_lvl not in STATES_NO_CHAT_SUPPORT:
            if TARGET_CHAT_ID:
                context.bot.send_message(chat_id=TARGET_CHAT_ID, text=message_formatting(update))
                context.bot.send_message(
                    text="Ваше сообщение было направленно в чат поддержки.",
                    reply_to_message_id=update.message.message_id
                )
                # update.message.reply_text(
                #     text="Ваше сообщение было направленно в чат поддержки.",
                #     reply_to_message_id=update.message.message_id,
                # )
            else:
                User.notify_admins(
                    update=update,
                    context=context,
                    message=notification_formatting(update=update),
                )


@not_for_banned_users
def end_asking_question(update: Update, context: CallbackContext) -> int:
    """End gathering of features and return to parent conversation."""
    user_data = context.user_data
    level = user_data[CURRENT_LEVEL]
    # if not user_data.get(level):
    #     user_data[level] = []
    # user_data[level].append(user_data[FEATURES])

    # Print upper level menu
    if level == QUESTION:
        user_data[START_OVER] = True
        onboarding_handlers.command_start(update, context)
    else:
        asking_question(update, context)

    return END
