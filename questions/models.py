from django.db import models
from users.models import User
from telegram import Update
from telegram.ext import CallbackContext


class Question(models.Model):
    msg_id = models.BigAutoField(primary_key=True)  # telegram_id
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    text = models.TextField()

    def __str__(self):
        return f'msg {self.msg_id} from {self.user}'


    @classmethod
    def add_question(cls, update: Update, context: CallbackContext):
        user, created = User.get_user_and_created(update=update, context=context)
        new_question, created = cls.objects.update_or_create(
            msg_id=update.message.message_id,
            user=user,
            text=update.message.text
        )
        return new_question, created
        # new_question.save()
        # bot_chats = cls.objects.all().values()
        # bot_chat_dict = {
        #     chat["chat_id"]: {
        #         "chat_name": chat["chat_name"],
        #         "is_support_chat": chat["is_support_chat"],
        #     }
        #     for chat in bot_chats
        # }
        return bot_chat_dict