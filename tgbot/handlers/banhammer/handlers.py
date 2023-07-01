from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import copy
from telegram.ext import CallbackContext
from users.models import User
from .keyboards import users_keyboard
from tgbot.handlers.onboarding import handlers as onboarding_handlers

from tgbot.states import BAN, BAN_LIST, END, CURRENT_LEVEL, START_OVER


def banhammer_button_press(update: Update, context: CallbackContext) -> str:
    context.user_data[CURRENT_LEVEL] = BAN
    display_users(update, context, page=1)
    user_data = context.user_data
    user_data[CURRENT_LEVEL] = BAN_LIST 
    return BAN_LIST


def display_users(update: Update, context: CallbackContext, page: int = None):
    message_text = "Администратор может забанить/разбанить отдельных участников или целую группу разом."
    query = update.callback_query
    query.answer()
    btn_captions = User.get_users_button_captions()
    rpl_mrkp = users_keyboard(btn_captions=btn_captions, page=page)
    update.callback_query.edit_message_text(
        text=message_text,
        reply_markup=rpl_mrkp,
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
    elif callback_data.startswith("item_"):
        # Обработка нажатия на кнопку с записью
        # username = int(callback_data.split("_")[1])
        cuted_callback_data = callback_data[5:]
        f_name, l_name, username = cuted_callback_data.split("_")
        # u = User.get_user_by_first_last_username(f_name, l_name, username)
        # btn_text = query.message.text
        original_reply_markup = update.callback_query.message.reply_markup 
        btn, reply_markup = find_button(update, callback_data)
        # if u:
            # u.is_blocked_bot = not u.is_blocked_bot
            # if u.is_blocked_bot:
        if not "🚫" in btn.text:
            btn.text += "🚫"
        else:
            btn.text = btn.text.replace("🚫", "")
        msg_test = update.callback_query.message.text
        if has_diff(update, reply_markup, callback_data):
            update.callback_query.edit_message_text(
                text=msg_test,
                reply_markup=reply_markup
            )


def has_diff(update: Update, new_markup: InlineKeyboardMarkup, callback_data: str):
    btn, original_reply_markup, indexes = find_button(
        update=update, callback_data=callback_data, make_copy=False, return_indexes=True
    )
    new_btn = new_markup._id_attrs[0][indexes[0]][indexes[1]]
    return btn.text != new_btn.text
    

 
def find_button(update: Update, callback_data: str, make_copy: bool = True, return_indexes: bool = False):
    need_btn = None
    if make_copy:
        reply_markup = copy.deepcopy(update.callback_query.message.reply_markup)
    else:
        reply_markup =update.callback_query.message.reply_markup
    buttons_list = reply_markup._id_attrs[0]
    indexes = None
    for i in range(3):
        for j, btn in enumerate(buttons_list[i]):
            if not need_btn and btn.callback_data == callback_data:
                need_btn = btn
                indexes = [i, j]
                break
        if need_btn:
            break
    if return_indexes and indexes:
        return need_btn, reply_markup, indexes
    else:
        return need_btn, reply_markup


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
