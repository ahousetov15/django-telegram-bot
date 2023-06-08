from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
from tgbot.states import BAN, BAN_LIST, END, CURRENT_LEVEL
from users.models import User
from .keyboards import users_keyboard
from tgbot.handlers.onboarding import handlers as onboarding_handlers


def banhammer_button_press(update: Update, context: CallbackContext) -> str:
    context.user_data[CURRENT_LEVEL] = BAN
    display_users(context, update, page=1)
    return BAN_LIST

def display_users(update: Update, context: CallbackContext, page: int = None):
    message_text = "Администратор может забанить/разбанить отдельных участников или целую группу разом."
    query = update.callback_query
    query.answer()
    btn_captions = User.get_users_button_captions()
    update.callback_query.edit_message_text(
        text=message_text, reply_markup=users_keyboard(btn_captions=btn_captions, page=page)
    )

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    if callback_data.startswith("prev_"):
        # Обработка нажатия на кнопку "Previous"
        page = int(callback_data.split("_")[1])
        new_page = page - 1 if page > 1 else 1
        display_users(update, context, new_page)

    elif callback_data.startswith("next_"):
        # Обработка нажатия на кнопку "Next"
        page = int(callback_data.split("_")[1])
        new_page = page + 1
        display_users(update, context, new_page)
    elif callback_data.startswith("ban_all"):
        User.ban_all()
        display_users(update, context, 1) 
    elif callback_data.startswith("save_ban"):
        User.bulk_save_is_blocked_bot()
        display_users(update, context, 1)
    else:
        # Обработка нажатия на кнопку с записью
        # username = int(callback_data.split("_")[1])
        f_name, l_name, username = callback_data.split("_")
        u = User.get_user_by_first_last_username(f_name, l_name, username)
        btn_text = query.message.text
        if u:
            u.is_blocked_bot = not u.is_blocked_bot
            if u.is_blocked_bot:
                btn_text+="🚫"
            else:
                btn_text.replace("🚫", "")

def end_banhammer(update: Update, context: CallbackContext) -> int:
    """End gathering of features and return to parent conversation."""
    user_data = context.user_data
    level = user_data[CURRENT_LEVEL]

    # Print upper level menu
    if level == BAN_LIST:
        user_data[START_OVER] = True
        onboarding_handlers.command_start(update, context)
    else:
        banhammer_button_press(update, context)

    return END