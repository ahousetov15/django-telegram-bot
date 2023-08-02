import logging
# from __future__ import annotations
from typing import Union, Optional, Tuple, List
from django.db import models
from django.db.models import QuerySet, Manager
from telegram import Update, error
from telegram.ext import CallbackContext
from tgbot.handlers.admin import static_text
from tgbot.handlers.utils.info import extract_user_data_from_update, extract_new_chat_members_from_update
from utils.models import CreateUpdateTracker, nb, CreateTracker, GetOrNoneManager
from dtb.settings import ADMINS_BY_DEFAULT
from tgbot.handlers.admin.static_text import welcome_message
from users.keyboards import welcome_user_keyboard
# from users.models import User
admins_by_default_int_list = map(int, ADMINS_BY_DEFAULT.split(','))


class AdminUserManager(Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_admin=True)


class User(CreateUpdateTracker):
    user_id = models.PositiveBigIntegerField(
        primary_key=True, verbose_name="Номер"
    )  # telegram_id
    username = models.CharField(max_length=32, **nb, verbose_name="Никнейм")
    first_name = models.CharField(max_length=256, **nb, verbose_name="Имя")
    last_name = models.CharField(max_length=256, **nb, verbose_name="Фамилия")
    language_code = models.CharField(
        max_length=8,
        help_text="Язык",
        verbose_name="Язык",
        **nb,
    )
    deep_link = models.CharField(
        max_length=64, **nb, verbose_name="Ссылка"
    )
    is_blocked_bot = models.BooleanField(default=False, verbose_name="Забанен(а)")
    is_admin = models.BooleanField(default=False, verbose_name="Админ")
    objects = GetOrNoneManager()  # user = User.objects.get_or_none(user_id=<some_id>)
    admins = AdminUserManager()  # User.admins.all()

    def __str__(self):
        return f"@{self.username}" if self.username is not None else f"{self.user_id}"

    @classmethod
    def get_admins(cls):
        return cls.admins

    @classmethod
    def get_admins_dict(cls):
        admins = cls.admins.values()
        admins_dict = {
            adm["user_id"]: {
                "username": adm["username"],
                "first_name": adm["first_name"],
                "last_name": adm["last_name"],
                "language_code": adm["language_code"],
                "deep_link": adm["deep_link"],
                "is_blocked_bot": adm["is_blocked_bot"],
            }
            for adm in admins
        }
        return admins_dict

    @classmethod
    def add_incoming_user(cls, update: Update, context: CallbackContext):
        data_list = extract_new_chat_members_from_update(update)
        # created_users = []
        for user in data_list:
            u, created = cls.objects.update_or_create(user_id=user["user_id"], defaults=user)
            if created:
                if str(user["user_id"]) in admins_by_default_int_list:
                    u.is_admin = True
                # Save deep_link to User model
                if (context is not None and context.args is not None and len(context.args) > 0):
                    payload = context.args[0]
                    if (str(payload).strip() != str(user["user_id"]).strip()):  # you can't invite yourself
                        u.deep_link = payload
                u.save()
                # User.send_welcome_message_and_keyboard(user=u, update=update, context=context)
    
    @classmethod
    def get_user_by_user_id(cls, user_id):
        users = cls.objects.filter(user_id=user_id)
        return users[0]  
    
    @classmethod
    def get_user_by_first_last_username(cls, first_n, last_n, username):
        users = cls.objects.filter(first_name=first_n, last_name=last_n, username=username)
        if len(users) != 1:
            return None
        return users[0]

    @classmethod
    def ban_all(cls):
        if cls.objects.exists():
            users = cls.objects.all()
            for user in users:
                if not user.is_admin:
                    user.is_blocked_bot = True
            User.objects.bulk_update(users, ["is_blocked_bot"])
        
    @classmethod
    def bulk_save_is_blocked_bot(cls):
        users = cls.objects.all()
        User.objects.bulk_update(users, ["is_blocked_bot"])


    @classmethod
    def get_users_button_captions(cls) -> List[dict]:
        btn_captions = [ 
            {
                "username": u["username"],
                "first_name": u["first_name"],
                "last_name": u["last_name"],
                "is_blocked_bot": u["is_blocked_bot"],
                "user_id": u["user_id"]
            }
            for u in cls.objects.order_by("first_name", "last_name").values()
        ]
        return btn_captions

    @classmethod
    def get_user_and_created(cls, update: Update, context: CallbackContext):
        """python-telegram-bot's Update, Context --> User instance"""
        data = extract_user_data_from_update(update)
        u, created = cls.objects.update_or_create(user_id=data["user_id"], defaults=data)
        if created:
            if str(data["user_id"]) in admins_by_default_int_list:
                u.is_admin = True
            # Save deep_link to User model
            if (context is not None and context.args is not None and len(context.args) > 0):
                payload = context.args[0]
                if (str(payload).strip() != str(data["user_id"]).strip()):  # you can't invite yourself
                    u.deep_link = payload
            u.save()
        return u, created

    @classmethod
    def get_users_id(cls) -> List[int]:
        all_users = cls.objects.all().values()
        users_id_list = [user["user_id"] for user in all_users]
        return users_id_list

    @classmethod
    def get_user(cls, update: Update, context: CallbackContext):
        u, _ = cls.get_user_and_created(update, context)
        return u

    @classmethod
    def notify_admins(cls, update: Update, context: CallbackContext, message: str):
        if admins_dict := cls.get_admins_dict():
            for admin_chat_id, admin_values in admins_dict.items():
                print(f"admin_chat_id : {admin_chat_id}, admin_values : {admin_values}")
                try:
                    context.bot.send_message(chat_id=admin_chat_id, text=message)
                except error.BadRequest as br:
                    print(f"Cannot send msg to admin: {admin_chat_id}, with data: {admin_values}: {br}")

    @classmethod
    def is_user_admin(cls, update: Update, context: CallbackContext):
        """
        Send 'only for admins' in case non admin user try to access and return False.
        
        Retunr True in otherwise
        """
        u = User.get_user(update, context)
        if not u.is_admin:
            context.bot.send_message(chat_id=u.user_id, text=static_text.only_for_admins_ru)
        return u.is_admin

    # @classmethod
    # def send_welcome_message_and_keyboard(cls, user: User, update: Update, context: CallbackContext):
    #     context.bot.send_message(chat_id=user.user_id, text=welcome_message, reply_markup=welcome_user_keyboard())

    # @classmethod
    # def send_welcome_message_and_keyboard_to_all(cls, bot: Bot):
    #     users_id_list = User.get_users_id()
    #     for user_id in users_id_list:
    #         try:
    #             bot.send_message(chat_id=user_id, text=welcome_message, reply_markup=welcome_user_keyboard())
    #         except error.Unauthorized as e:
    #             logging.error(f"Пользователь с id={user_id} возможно не авторизован. Невозможно начать с ним беседу.", exc_info=str(e))
    #         except Exception as e:
    #             logging.error(f"Непонятное исключение.", exc_info=str(e))

    @classmethod
    def get_user_by_username_or_user_id(cls, username_or_user_id: Union[str, int]):
        """Search user in DB, return User or None if not found"""
        username = str(username_or_user_id).replace("@", "").strip().lower()
        if username.isdigit():  # user_id
            return cls.objects.filter(user_id=int(username)).first()
        return cls.objects.filter(username__iexact=username).first()

    @property
    def invited_users(self):
        return User.objects.filter(deep_link=str(self.user_id), created_at__gt=self.created_at)

    @property
    def tg_str(self) -> str:
        if self.username:
            return f"@{self.username}"
        return f"{self.first_name} {self.last_name}" if self.last_name else f"{self.first_name}"


class Location(CreateTracker):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()

    objects = GetOrNoneManager()

    def __str__(self):
        return f"user: {self.user}, created at {self.created_at.strftime('(%H:%M, %d %B %Y)')}"
