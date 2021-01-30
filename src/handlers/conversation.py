from handlers.categories import (
    choose_category,
    get_categories,
    remove_category,
    set_category,
    choose_or_create_category
)
from handlers.start import set_link, handler_start
from handlers.empty import not_implemented
from handlers.entry import category, domain, link, main, process
from handlers.domains import get_domains, choose_domain, remove_domain, sync_domain
from handlers.process import next_or_stop
from handlers.links import get_links
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
                CommandHandler("category", category),
                CommandHandler("domain", domain),
                CommandHandler("process", process),
                CommandHandler("link", link),
                MessageHandler(Filters.all, main),
            ],
            states={
                START: [MessageHandler(Filters.all & (~Filters.command), handler_start)],
                CATEGORY: [
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY), ), get_categories),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_REMOVE_KEY), ), choose_category),
                    MessageHandler(Filters.all, not_implemented)
                ],
                DOMAIN: [
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY), ), get_domains),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_REMOVE_KEY), ), choose_domain),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_SYNC_KEY), ), sync_domain),
                    MessageHandler(Filters.all, not_implemented)
                ],
                LINK: [
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY), ), get_links),
                    MessageHandler(Filters.all, not_implemented)
                ],
                CHOOSING: [
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_MANUAL_KEY)), next_or_stop),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_AUTO_KEY)), choose_or_create_category),
                    MessageHandler(Filters.all, not_implemented)
                ],
                SET_CATEGORY: [MessageHandler(Filters.all, set_category)],
                SET_LINK: [MessageHandler(Filters.all, set_link)],
                RM_CATEGORY: [MessageHandler(Filters.all, remove_category)],
                RM_DOMAIN: [MessageHandler(Filters.all, remove_domain)],
            },
            fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
        )
