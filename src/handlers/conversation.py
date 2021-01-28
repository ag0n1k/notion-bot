from handlers.categories import (
    choose_category,
    get_categories,
    handler_category,
    remove_category,
    set_category
)
from handlers.start import set_link, handler_start
from handlers.entry import handler_entry
from handlers.process import handler_process, next_or_stop
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)

from helpers.constants import *


def done(update, context) -> int:
    update.message.reply_text("Something went wrong...")
    return ConversationHandler.END


class Conversation:
    def __init__(self, commands=("start", "categories", "links")):
        self.conversation = ConversationHandler(
            entry_points=[
                CommandHandler("start", handler_start),
                CommandHandler("category", handler_category),
                CommandHandler("process", handler_process),
            ],
            states={
                START: [MessageHandler(Filters.all & (~Filters.command), handler_start)],
                ENTRY: [MessageHandler(Filters.all & (~Filters.command), handler_category)],
                SET_LINK: [MessageHandler(Filters.all, set_link)],
                CHOOSING: [
                    MessageHandler(Filters.regex('^({}})$'.format(KEYBOARD_NEXT_KEY)), handler_entry),
                    MessageHandler(Filters.regex('^({}})$'.format(KEYBOARD_MANUAL_KEY)), next_or_stop),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_AUTO_KEY)), set_category),
                ],
                CATEGORY: [
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY), ), get_categories),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_REMOVE_KEY), ), choose_category),
                ],
                SET_CATEGORY: [MessageHandler(Filters.all, set_category)],
                RM_CATEGORY: [MessageHandler(Filters.all, remove_category)],
            },
            fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
        )
