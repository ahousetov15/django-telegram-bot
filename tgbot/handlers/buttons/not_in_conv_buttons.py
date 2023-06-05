from telegram import Update
from telegram.ext import CallbackContext


def handle_button_press(update: Update, context: CallbackContext):
    query = update.callback_query

    # Обработка нажатия кнопки
    # ...

    if not context.user_data.get("CURRENT_LEVEL"):
        # query.answer(
        #     text=f"Вы нажали кнопку, но беседа с ботом не начата. Нажмите кнопка выбора команд в левом нижнем углу и выберите /start"
        # )
        update.callback_query.message.reply_text(
            text=f"Вы нажали кнопку, но беседа с ботом не начата. Нажмите кнопка выбора команд в левом нижнем углу и выберите /start"
        )