from telegram import Update
from telegram.ext import CallbackContext
from users.models import User, Location


def handle_button_press(update: Update, context: CallbackContext):
    if not context.user_data.get("CURRENT_LEVEL"):
        # query.answer(
        #     text=f"Вы нажали кнопку, но беседа с ботом не начата. Нажмите кнопка выбора команд в левом нижнем углу и выберите /start"
        # )
        # update.callback_query.message.reply_text(
        u = User.get_user(update, context)
        context.bot.send_message(
            chat_id=u.user_id,
            text=f"Вы нажали кнопку, но беседа с ботом не начата. Нажмите кнопка выбора команд в левом нижнем углу и выберите /start"
        )