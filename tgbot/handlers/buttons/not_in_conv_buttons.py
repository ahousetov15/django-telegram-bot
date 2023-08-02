from telegram import Update
from telegram.ext import CallbackContext
from users.models import User, Location
from tgbot.states import END
from tgbot.handlers.main import not_for_banned_users


@not_for_banned_users
def handle_button_press(update: Update, context: CallbackContext):
    cur_lvl = context.user_data.get("CURRENT_LEVEL")
    if not cur_lvl or cur_lvl == END:
        u = User.get_user(update, context)
        context.bot.send_message(
            chat_id=u.user_id,
            text=f"Вы нажали кнопку, но беседа с ботом не начата. Нажмите кнопка выбора команд в левом нижнем углу и выберите /start",
        )
