from telegram import Update
from telegram.ext import CallbackContext
from chats.models import Chats
from users.models import User
from dtb.settings import MSK_TZ


def ask_question(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    context.user_data["waiting_for_question"] = True
    query.edit_message_text("Пожалуйста, введите ваш вопрос.")


def question_formatting(update: Update):
    result = f"#вопрос\n"
    result += f"от пользователя: {update.message.from_user.full_name}\n"
    result += f"логин: {update.message.from_user.name}\n"
    result += f"задан: {update.message.date.astimezone(MSK_TZ).strftime('%Y-%m-%d %H:%M:%S')} по Москве"
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
    result = f"получено сообщение или вопрос от пользователя, но чат поддержки не указан. Пожалуйста, укажите чат поддержки или все сообщения будут пересылаться сюда.\n\n"
    result += f"от пользователя: {update.message.from_user.full_name}\n"
    result += f"логин: {update.message.from_user.name}\n"
    result += f"отправлено в {update.message.date.astimezone(MSK_TZ).strftime('%Y-%m-%d %H:%M:%S')} по Москве"
    result += f"\n\n{update.message.text}"
    return result


def handle_message_or_question(update: Update, context: CallbackContext):
    TARGET_CHAT_ID = Chats.get_support_chat_id()
    if (
        "waiting_for_question" in context.user_data
        and context.user_data["waiting_for_question"]
    ):
        if TARGET_CHAT_ID:
            context.bot.send_message(
                chat_id=TARGET_CHAT_ID, text=question_formatting(update)
            )
        else:
            User.notify_admins(
                update=update,
                context=context,
                message=notification_formatting(update=update),
            )

        update.message.reply_text(
            text="Ваш вопрос был успешно отправлен.",
            reply_to_message_id=update.message.message_id,
        )
        context.user_data["waiting_for_question"] = False
    else:
        if TARGET_CHAT_ID:
            context.bot.send_message(
                chat_id=TARGET_CHAT_ID, text=message_formatting(update)
            )
            update.message.reply_text(
                text="Ваше сообщение было направленно в чат поддержки.",
                reply_to_message_id=update.message.message_id,
            )
        else:
            User.notify_admins(
                update=update,
                context=context,
                message=notification_formatting(update=update),
            )
