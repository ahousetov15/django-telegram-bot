from django.db import models
from users.models import User


class Question(models.Model):
    msg_id = models.BigAutoField(primary_key=True)  # telegram_id
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    text = models.TextField()

    def __str__(self):
        return f'{self.chat_name}' if self.chat_name is not None else f'chat {self.chat_id}'
