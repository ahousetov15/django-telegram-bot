from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .static_text import EMOJI_MARKED
from tgbot.states import SUPPORT_CHAT, SELECT_SUPPORT_CHAT, SUPPORT_CHAT_AND_NUMBER, END

NUMBER_BUTTONS_IN_LINE = 3


def keyboard_bot_chats(chats: dict) -> InlineKeyboardMarkup:
    buttons = []
    if chats:
        line = -1
        for num, (chat_id, values) in enumerate(chats.items()):
            if num % NUMBER_BUTTONS_IN_LINE == 0:
                buttons.append([])
                line = len(buttons) - 1
            btn_name = values["chat_name"]
            if values["is_support_chat"]:
                btn_name += EMOJI_MARKED
            buttons[line].append(
                InlineKeyboardButton(
                    btn_name, callback_data=f"{SUPPORT_CHAT}_{chat_id}"
                )
            )
        line += 1
        buttons.append([])
        buttons[line].append(InlineKeyboardButton("Назад.", callback_data=str(END)))
    return InlineKeyboardMarkup(buttons)
