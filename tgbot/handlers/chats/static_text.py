EMOJI_MARKED = " ✅"
SUPPORT_CHAT_SET = (
    f"\n\n Чат поддержки установлен. При желании вы можете назначить другой чат."
)
SUPPORT_CHAT_UNSET = f"\n\nК сожалению, чат поддержки не установлен. Пожалуйста, установите его, выбрав один из списка."


def chat_exists_in_number(number: str):
    chat_numerals = None
    if number.endswith("1"):
        chat_numerals = "чате"
    else:
        chat_numerals = "чатах"
    return (
        f"Вот список чатов, где состоит бот. На данный момент он состоит в {number} "
        + chat_numerals
        + "."
    )

NO_CHATS = f"Бот не состоит ни в одном чате. Пожалуйста, добавьте его в группы. Последняя группа куда будет добавлен бот станет чатом поддержки. Изменить чат поддержки можно в соответствующем меню."
