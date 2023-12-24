from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
import copy
from telegram.ext import CallbackContext
from users.models import User
from .keyboards import users_keyboard
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.main import not_for_banned_users, only_for_admin
from dtb.settings import ADMINS_BY_DEFAULT
from tgbot.states import BAN, BAN_LIST, END, CURRENT_LEVEL, START_OVER, BANHAMMER_REPLY_MARKUP
from const import ADMINS_BY_DEFAULT_INT_LIST
# ADMINS_BY_DEFAULT_INT_LIST = [159041507, 151854871] 



@not_for_banned_users
@only_for_admin
def banhammer_button_press(update: Update, context: CallbackContext) -> str:
    if User.is_user_admin(update=update, context=context):
        context.user_data[CURRENT_LEVEL] = BAN
        display_users(update, context, page=1)
        user_data = context.user_data
        user_data[CURRENT_LEVEL] = BAN_LIST
        return BAN_LIST
	
	
def display_users(update: Update, context: CallbackContext, page: int = None):
    message_text = "Администратор может забанить/разбанить отдельных участников или целую группу разом."
    query = update.callback_query
    query.answer()
    user_data = context.user_data 
    btn_captions = User.get_users_button_captions()
    rpl_mrkp = users_keyboard(btn_captions=btn_captions, page=page)
    if not BANHAMMER_REPLY_MARKUP in user_data:
        user_data[BANHAMMER_REPLY_MARKUP] = None
    if user_data.get(BANHAMMER_REPLY_MARKUP) != rpl_mrkp:
        user_data[BANHAMMER_REPLY_MARKUP] = rpl_mrkp
        update.callback_query.edit_message_text(
            text=message_text,
            reply_markup=rpl_mrkp,
        )


@not_for_banned_users
@only_for_admin
def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    callback_data = query.data
    new_page = 1
    who_try_ban = None 
    try:
        who_try_ban = update.effective_user
    except Exception as e:
        raise e("There is no 'effective_user' in update")
    if callback_data.startswith("prev_"):
        # Обработка нажатия на кнопку "Previous"
        page = int(callback_data.split("_")[1])
        new_page = page - 1 if page > 1 else 1
        # display_users(update, context, new_page)
    elif callback_data.startswith("next_"):
        # Обработка нажатия на кнопку "Next"
        page = int(callback_data.split("_")[1])
        new_page = page + 1
        # display_users(update, context, new_page)
    elif callback_data.startswith("ban_all"):
        User.ban_all()
        # display_users(update, context, 1)
    elif callback_data.startswith("save_ban"):
        User.bulk_save_is_blocked_bot()
        # display_users(update, context, 1)
    elif callback_data.startswith("item_"):
        # Обработка нажатия на кнопку с записью
        user_id = callback_data[5:]
        u = User.get_user_by_user_id(user_id=user_id)
        if u:
            if u.user_id == who_try_ban.id:
                context.bot.send_message(
                    chat_id=u.user_id,
                    text="Не получится забанить самого себя 🙂",
                )
                return
            elif int(u.user_id) in ADMINS_BY_DEFAULT_INT_LIST:
                context.bot.send_message(
                    chat_id=u.user_id,
                    text="Этого человека банить нельзя. 😎",
                )
                return
            else:
                u.is_blocked_bot = not u.is_blocked_bot
                u.save()
                new_page = find_button_page(update=update, callback_data=callback_data)
    display_users(update, context, new_page)    


# def has_diff(update: Update, new_markup: InlineKeyboardMarkup, callback_data: str):
#     btn, original_reply_markup, indexes = find_button(
#         update=update, callback_data=callback_data, make_copy=False, return_indexes=True
#     )
#     new_btn = new_markup._id_attrs[0][indexes[0]][indexes[1]]
#     return btn.text != new_btn.text
    


def find_button_page(update: Update, callback_data: str) -> int:
    counter_btn = None
    page = '1'
    reply_markup =update.callback_query.message.reply_markup
    buttons_list = reply_markup._id_attrs[0]
    for level in buttons_list:
        for btn in level:
            if btn.callback_data == "counter":
                counter_btn = btn
                break
        if counter_btn:
            break
    if counter_btn:
        page = counter_btn.text.split("/")[0]
    return int(page)


@not_for_banned_users
@only_for_admin
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
