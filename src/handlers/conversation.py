from handlers.categories import choose_category, get_categories, handler_category, remove_category
from handlers.start import set_link, handler_start
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
            ],
            states={
                ENTRY: [MessageHandler(Filters.all & (~Filters.command), handler_category)],
                SET_LINK: [MessageHandler(Filters.all, set_link)],
                CATEGORY: [
                    MessageHandler(Filters.regex('^{}$'.format(KEYBOARD_GET_KEY),), get_categories),
                    MessageHandler(Filters.regex('^{}$'.format(KEYBOARD_REMOVE_KEY), ), choose_category),
                ],
                RM_CATEGORY: [MessageHandler(Filters.all, remove_category)],
            },
            fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
        )
