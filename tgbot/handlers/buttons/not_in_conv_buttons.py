from telegram import Update
from telegram.ext import CallbackContext
from users.models import User, Location
from tgbot.states import END
from tgbot.handlers.main import not_for_banned_users
import logging
import pprint

logger = logging.getLogger(__name__)
pp = pprint.PrettyPrinter(indent=4)


@not_for_banned_users
def handle_button_press(update: Update, context: CallbackContext):
    logger.debug(f"+++handle_button_press+++")
    cur_lvl = context.user_data.get("CURRENT_LEVEL")
    logger.debug(f"cur_lvl: {cur_lvl}")
    logger.debug(f"not cur_lvl or cur_lvl == END: {not cur_lvl or cur_lvl == END}")
    if not cur_lvl or cur_lvl == END:
        u = User.get_user(update, context)
        logger.debug(f"cur_lvl: {cur_lvl}")
        context.bot.send_message(
            chat_id=u.user_id,
            text=f"Вы нажали кнопку, но беседа с ботом не начата. Нажмите кнопка выбора команд в левом нижнем углу и выберите /start",
        )
    logger.debug(f"---handle_button_press---")
