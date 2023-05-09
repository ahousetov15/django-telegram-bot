from django.db import models
from telegram import Update
from telegram.ext import CallbackContext
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager
from typing import Union, Optional, Tuple
from dtb.settings import TELEGRAM_BOT_USERNAME
from django.forms.models import model_to_dict


class Chats(models.Model):
    chat_id = models.BigAutoField(primary_key=True)  # telegram_id
    chat_name = models.CharField(max_length=1024, **nb)
    is_support_chat = models.BooleanField(default=False)

    objects = GetOrNoneManager()

    def __str__(self):
        return (
            f"{self.chat_name}"
            if self.chat_name is not None
            else f"chat {self.chat_id}"
        )

    @classmethod
    def chats_to_dict(cls):
        bot_chats = cls.objects.all().values()
        bot_chat_dict = {
            chat["chat_id"]: {
                "chat_name": chat["chat_name"],
                "is_support_chat": chat["is_support_chat"],
            }
            for chat in bot_chats
        }
        return bot_chat_dict

    @classmethod
    def add_chat(cls, update: Update, context: CallbackContext) -> Tuple[dict, bool]:
        """Если бота добавили в чат, нужно добавить его в БД"""
        chat_id = update.message.chat_id
        chat_name = update._effective_message.chat.title
        bot_chats = cls.chats_to_dict()
        for member in update.message.new_chat_members:
            if member.username == TELEGRAM_BOT_USERNAME:
                if chat_id not in bot_chats:
                    chat, created = cls.objects.update_or_create(
                        chat_id=chat_id, chat_name=chat_name
                    )
                    if created:
                        chat.save()
                        return model_to_dict(chat), created
        return None, False

    @classmethod
    def remove_chat(cls, update: Update, context: CallbackContext) -> Tuple[Union[str, None], Union[dict, None]]:
        """Если бот удалили(удалился) из чата, нужно убраться его из БД"""
        removed = None
        chat_id = update.message.chat_id
        bot_chats = cls.chats_to_dict()
        if update.message.left_chat_member.username == TELEGRAM_BOT_USERNAME:
            if chat_id in bot_chats:
                cls.objects.filter(chat_id=chat_id).delete()
                removed = chat_id, bot_chats[chat_id]
        return removed
