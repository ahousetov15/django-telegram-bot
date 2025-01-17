EMOJI_MARKED = " ✅"
SUPPORT_CHAT_SET = (
    f"\n\nЧат поддержки установлен. При желании вы можете назначить другой чат."
)
SUPPORT_CHAT_UNSET = f"\n\nК сожалению, чат поддержки не установлен. Пожалуйста, установите его, выбрав один из списка."


def chat_exists_in_number(number: str):
    chat_numerals = None
    if number.endswith("1"):
        chat_numerals = "чате"
    else:
        chat_numerals = "чатах"
    return (
        f"Вы находись в 'Чатах поддержки'. \nЧат поддержки - отдельный чат, в котором состоит бот(добавьте его), куда пересылаются сообщения от пользователей. Сообщения заданные как 'вопрос' не учитываются. \n\n"
        + f"На данный момент, бот состоит в  {number} "
        + chat_numerals
        + "."
    )


NO_CHATS = f"Бот не состоит ни в одном чате. Пожалуйста, добавьте его в группы. Последняя группа куда будет добавлен бот станет чатом поддержки. Изменить чат поддержки можно в соответствующем меню."
