"""
Telegram event handlers
"""
from telegram.ext import (
    Dispatcher,
    Filters,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
)
from dtb.settings import DEBUG
from tgbot.handlers.broadcast_message.manage_data import CONFIRM_DECLINE_BROADCAST
from tgbot.handlers.broadcast_message.static_text import broadcast_command
from tgbot.handlers.onboarding.manage_data import SECRET_LEVEL_BUTTON
from tgbot.handlers.utils import error
from tgbot.handlers.admin import handlers as admin_handlers
from tgbot.handlers.location import handlers as location_handlers
from tgbot.handlers.onboarding import handlers as onboarding_handlers
from tgbot.handlers.broadcast_message import handlers as broadcast_handlers
from tgbot.handlers.status_update import handlers as status_update_handlers
from tgbot.handlers.message import handlers as message_handlers
from tgbot.handlers.chats import handlers as chats_handlers
from tgbot.handlers.buttons import not_in_conv_buttons
from tgbot.handlers.banhammer import handlers as banhammer_handler
from tgbot.main import bot
from tgbot.states import (
    SELECTING_ACTION,
    QUESTION,
    ASKING_QUESTION,
    HELP,
    EXPORT_QUESTIONS,
    SUPPORT_CHAT,
    SELECT_SUPPORT_CHAT,
    SUPPORT_CHAT_AND_NUMBER,
    STOP_BOT,
    SELECTING_LEVEL,
    SELECTING_SUPPORT_CHAT,
    SELECT_STOP_BOT,
    SELECT_STOP_AND_REMOVE_ALL,
    SELECTING_FEATURE,
    TYPING,
    STOPPING,
    SHOWING,
    END,
    HAS_QUESTION,
    BAN,
    BAN_LIST,
    PREV_, NEXT_, BAN_ALL, SAVE_BAN, ITEM_
)


def setup_dispatcher(dp):
    """
    Adding handlers for events from Telegram
    """
    # invite or leave chat handlers
    dp.add_handler(
        MessageHandler(
            Filters.status_update.new_chat_members,
            status_update_handlers.add_bot_to_chat,
        )
    )
    dp.add_handler(
        MessageHandler(
            Filters.status_update.left_chat_member,
            status_update_handlers.remove_bot_from_chat,
        )
    )

    banhammer_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                banhammer_handler.banhammer_button_press, pattern="^" + str(BAN) + "$"
            )
        ],
        states={
            BAN_LIST: [
                CallbackQueryHandler(
                    banhammer_handler.handle_callback, pattern="^"+str(PREV_)+"$"
                ),
                CallbackQueryHandler(
                    banhammer_handler.handle_callback, pattern="^"+str(NEXT_)+"$"
                ),
                CallbackQueryHandler(
                    banhammer_handler.handle_callback, pattern="^"+str(BAN_ALL)+"$"
                ),
                CallbackQueryHandler(
                    banhammer_handler.handle_callback, pattern="^"+str(SAVE_BAN)+"$"
                ),
                CallbackQueryHandler(
                    banhammer_handler.handle_callback, pattern="^"+str(ITEM_)+"$"
                ),
            ]
        },
        fallbacks=[
            CallbackQueryHandler(
                banhammer_handler.end_banhammer, pattern="^" + str(END) + "$"
            ),
            CommandHandler("stop", onboarding_handlers.stop_main_conv),
        ],
        map_to_parent={
            # Возвращаемся к основному диалогу.
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: STOPPING,
        },
    )

    # support_chats_conv = ConversationHandler(
    #     entry_points=[
    #         CallbackQueryHandler(
    #             chats_handlers.list_sup_chat, pattern="^" + str(SUPPORT_CHAT) + "$"
    #         )
    #     ],
    #     states={
    #         SUPPORT_CHAT: [
    #             CallbackQueryHandler(
    #                 chats_handlers.list_sup_chat, pattern="^" + str(SUPPORT_CHAT) + "$"
    #             )
    #         ],
    #         SELECT_SUPPORT_CHAT: [
    #             CallbackQueryHandler(
    #                 chats_handlers.handle_support_chat,
    #                 pattern=f"^{SUPPORT_CHAT_AND_NUMBER}",
    #                 pass_user_data=True,
    #             )
    #         ],
    #     },
    #     fallbacks=[
    #         CallbackQueryHandler(
    #             chats_handlers.end_support_chat, pattern="^" + str(END) + "$"
    #         ),
    #         CommandHandler("stop", onboarding_handlers.stop_main_conv),
    #     ],
    #     map_to_parent={
    #         # Возвращаемся к основному диалогу.
    #         END: SELECTING_ACTION,
    #         # End conversation altogether
    #         STOPPING: STOPPING,
    #     },
    # )

    ask_question_conv = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(
                message_handlers.ask_question_button_press,
                pattern="^" + str(QUESTION) + "$",
            )
        ],
        states={
            ASKING_QUESTION: [
                CallbackQueryHandler(
                    message_handlers.asking_question,
                    pattern="^" + str(ASKING_QUESTION) + "$",
                )
            ],
            TYPING: [
                MessageHandler(Filters.text, message_handlers.handle_only_questions)
            ],
        },
        fallbacks=[
            CallbackQueryHandler(
                message_handlers.end_asking_question, pattern="^" + str(END) + "$"
            ),
            CommandHandler("stop", onboarding_handlers.stop_main_conv),
        ],
        map_to_parent={
            # Возвращаемся к основному диалогу.
            END: SELECTING_ACTION,
            # End conversation altogether
            STOPPING: STOPPING,
        },
    )

    selection_handlers = [
        ask_question_conv,
        # support_chats_conv,
        CallbackQueryHandler(
            message_handlers.export_questions, pattern="^" + str(EXPORT_QUESTIONS) + "$"
        ),
        banhammer_conv,
        CallbackQueryHandler(
            onboarding_handlers.stop_main_conv, pattern="^" + str(END) + "$"
        )
    ]

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", onboarding_handlers.command_start)],
        states={
            SELECTING_ACTION: selection_handlers,
            QUESTION: [ask_question_conv],
            # SUPPORT_CHAT: [support_chats_conv],
            BAN: [banhammer_conv],
            STOPPING: [CommandHandler("start", onboarding_handlers.command_start)],
        },
        fallbacks=[
            CallbackQueryHandler(
                onboarding_handlers.stop_main_conv, pattern="^" + str(END) + "$"
            ),  # по большому счету не нужен, т.к. отрабатывает в selection_handlers
            CommandHandler("stop", onboarding_handlers.stop_main_conv),
        ],
    )

    dp.add_handler(conv_handler)

    # admin commands
    # dp.add_handler(CommandHandler("admin", admin_handlers.admin))
    # dp.add_handler(CommandHandler("stats", admin_handlers.stats))
    # dp.add_handler(CommandHandler('export_users', admin_handlers.export_users))

    # processing msg or questions
    dp.add_handler(
        MessageHandler(Filters.text, message_handlers.handle_message_or_question)
    )

    # Обработка нажатия кнопок, вне контекста беседы.
    dp.add_handler(CallbackQueryHandler(not_in_conv_buttons.handle_button_press))

    # //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    # # location
    # dp.add_handler(CommandHandler("ask_location", location_handlers.ask_for_location))
    # dp.add_handler(MessageHandler(Filters.location, location_handlers.location_handler))

    # # secret level
    # dp.add_handler(CallbackQueryHandler(onboarding_handlers.secret_level, pattern=f"^{SECRET_LEVEL_BUTTON}"))

    # # broadcast message
    # dp.add_handler(
    #     MessageHandler(Filters.regex(rf'^{broadcast_command}(/s)?.*'), broadcast_handlers.broadcast_command_with_message)
    # )
    # dp.add_handler(
    #     CallbackQueryHandler(broadcast_handlers.broadcast_decision_handler, pattern=f"^{CONFIRM_DECLINE_BROADCAST}")
    # )

    # # files
    # dp.add_handler(MessageHandler(
    #     Filters.animation, files.show_file_id,
    # ))

    # handling errors
    dp.add_error_handler(error.send_stacktrace_to_tg_chat)

    # EXAMPLES FOR HANDLERS
    # dp.add_handler(MessageHandler(Filters.text, <function_handler>))
    # dp.add_handler(MessageHandler(
    #     Filters.document, <function_handler>,
    # ))
    # dp.add_handler(CallbackQueryHandler(<function_handler>, pattern="^r\d+_\d+"))
    # dp.add_handler(MessageHandler(
    #     Filters.chat(chat_id=int(TELEGRAM_FILESTORAGE_ID)),
    #     # & Filters.forwarded & (Filters.photo | Filters.video | Filters.animation),
    #     <function_handler>,
    # ))

    return dp


n_workers = 0 if DEBUG else 4
dispatcher = setup_dispatcher(
    Dispatcher(bot, update_queue=None, workers=n_workers, use_context=True)
)
