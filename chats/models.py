from django.db import models
from django.db.models import Q
from telegram import Update
from telegram.ext import CallbackContext
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager
from typing import Union, Optional, Tuple
from dtb.settings import TELEGRAM_BOT_USERNAME
from django.forms.models import model_to_dict


class Chats(models.Model):
    class Meta:
        verbose_name_plural = "Chats"

    chat_id = models.BigAutoField(
        primary_key=True, verbose_name="Номер чата"
    )  # telegram_id
    chat_name = models.CharField(max_length=1024, **nb, verbose_name="Название")
    is_support_chat = models.BooleanField(default=False, verbose_name="Чат поддержки")

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
    def get_support_chat_id(cls):
        try:
            support_chat = cls.objects.get(is_support_chat=True)
            return support_chat.chat_id
        except models.Model.DoesNotExist:
            return None

    @classmethod
    def set_chat_as_support(cls, chat_id):
        not_support_chats = list(cls.objects.filter(~Q(chat_id=chat_id)))
        for chat in not_support_chats:
            chat.is_support_chat = False
        cls.objects.bulk_update(not_support_chats, ["is_support_chat"])
        new_support_chat = cls.objects.get(chat_id=chat_id)
        new_support_chat.is_support_chat = True
        new_support_chat.save()

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
                        cls.set_chat_as_support(chat_id)
                        return model_to_dict(chat), created
        return None, False

    @classmethod
    def remove_chat(
        cls, update: Update, context: CallbackContext
    ) -> Tuple[Union[str, None], Union[dict, None]]:
        """Если бот удалили(удалился) из чата, нужно убраться его из БД"""
        removed = None
        chat_id = update.message.chat_id
        bot_chats = cls.chats_to_dict()
        if update.message.left_chat_member.username == TELEGRAM_BOT_USERNAME:
            if chat_id in bot_chats:
                cls.objects.filter(chat_id=chat_id).delete()
                removed = chat_id, bot_chats[chat_id]
        return removed
