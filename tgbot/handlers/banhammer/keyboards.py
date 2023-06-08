from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ContextTypes
from users.models import User
from typing import List

ITEMS_PER_PAGE = 6  # Количество записей на одной странице

def users_keyboard(btn_captions: List[dict], page: int) -> InlineKeyboardMarkup:
    start_index = (page - 1) * ITEMS_PER_PAGE
    end_index = start_index + ITEMS_PER_PAGE

    items_to_display = btn_captions[start_index:end_index]

    # Создать InlineKeyboard с кнопками для каждой записи
    keyboard = []
    for item in items_to_display:
        btn_text = f"{item['first_name']}_{item['last_name']}_{item['username']}"
        if item['is_blocked_bot']:
            btn_text+="🚫"
        button = InlineKeyboardButton(btn_text, callback_data=f"item_{item['username']}")
        keyboard.append([button])
    
    # Добавить кнопки пагинации
    btn_count = len(btn_captions)
    if btn_count <= ITEMS_PER_PAGE:
        page_count = 1
    else:
        page_count = (btn_count%ITEMS_PER_PAGE)+1
        
    prev_button = InlineKeyboardButton("⬅️", callback_data=f"prev_{page}")
    counter = InlineKeyboardButton(f"{page}/{page_count}")
    next_button = InlineKeyboardButton("⬅️", callback_data=f"next_{page}")
    save_btn = InlineKeyboardButton("Сохранить✅️️️️️️️", callback_data=f"save_ban")
    ban_all_btn = InlineKeyboardButton("Забанить всех", callback_data=f"ban_all")
    keyboard.append([ban_all_btn])
    keyboard.append([save_btn])
    keyboard.append([prev_button, counter, next_button])

    # reply_markup = InlineKeyboardMarkup(keyboard)

    # # Отправить сообщение с InlineKeyboard
    # update.message.reply_text("Select an item:", reply_markup=reply_markup)

    return InlineKeyboardMarkup(keyboard)