from django.contrib import admin
from chats.models import Chats


@admin.register(Chats)
class ChatsAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'chat_name', 'is_support_chat']
    search_fields = ('chat_id', 'chat_name')
