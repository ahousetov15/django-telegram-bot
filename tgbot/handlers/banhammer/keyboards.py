import copy
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from typing import List

ITEMS_PER_PAGE = 9  # Количество записей на одной странице
ITEMS_PER_LINE = 3
def users_keyboard(btn_captions: List[dict], page: int) -> InlineKeyboardMarkup:
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    items_to_display = btn_captions[start_index:end_index]

    # Создать InlineKeyboard с кнопками для каждой записи
    keyboard = []
    row = []
    for item in items_to_display:
        # btn_text = f"{item['first_name']}_{item['last_name']}_{item['username']}"
        btn_text = f"{item['first_name']}_{item['last_name']}"
        if item['is_blocked_bot']:
            btn_text+=f"🚫"
        button = InlineKeyboardButton(text=btn_text, callback_data=f"item_{item['username']}")
        if len(row) == ITEMS_PER_LINE:
            keyboard.append([btn for btn in row])
            row.clear()
        else:
            row.append(button)
    if len(row) > 0:
        keyboard.append([btn for btn in row])
        row.clear()
    
    # Добавить кнопки пагинации
    btn_count = len(btn_captions)
    if btn_count <= ITEMS_PER_PAGE:
        page_count = 1
    else:
        page_count = (btn_count%ITEMS_PER_PAGE)+1
        
    prev_button = InlineKeyboardButton(text=f"⬅️", callback_data=f"prev_{page}")
    counter = InlineKeyboardButton(text=f"{page}/{page_count}", callback_data=f"counter")
    next_button = InlineKeyboardButton(text=f"⬅️", callback_data=f"next_{page}")
    save_btn = InlineKeyboardButton(text=f"Сохранить", callback_data=f"save_ban")
    ban_all_btn = InlineKeyboardButton(text=f"Забанить всех", callback_data=f"ban_all")
    keyboard.append([ban_all_btn])
    keyboard.append([save_btn])
    keyboard.append([prev_button, counter, next_button])
    # keyboard.append([prev_button, next_button])

    # reply_markup = InlineKeyboardMarkup(keyboard)

    # # Отправить сообщение с InlineKeyboard
    # update.message.reply_text("Select an item:", reply_markup=reply_markup)

    # return ReplyKeyboardMarkup(keyboard)
    return InlineKeyboardMarkup(keyboard)