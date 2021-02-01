import base.utils
import handlers.category
import handlers.domain
import handlers.empty
import handlers.entry
import handlers.link
import handlers.process
import handlers.status

from base.constants import *

from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters
)


class NBotConversation:
    conversation = ConversationHandler(
        entry_points=[
            CommandHandler("category", handlers.entry.category),
            CommandHandler("domain", handlers.entry.domain),
            CommandHandler("link", handlers.entry.link),
            CommandHandler("process", handlers.entry.process),
            CommandHandler("start", handlers.entry.start),
            CommandHandler("status", handlers.entry.status),
            MessageHandler(Filters.all, handlers.entry.main),
        ],
        states={
            START: [MessageHandler(Filters.all, handlers.entry.start)],
            CATEGORY: [
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY)), handlers.category.get),
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_REMOVE_KEY)), handlers.category.choose),
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_SYNC_KEY)), handlers.category.sync),
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_UPDATE_KEY)), handlers.category.sync_update),
                MessageHandler(Filters.all, handlers.empty.not_implemented)
            ],
            DOMAIN: [
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY)), handlers.domain.get),
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_REMOVE_KEY)), handlers.domain.choose),
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_SYNC_KEY)), handlers.domain.sync),
                MessageHandler(Filters.all, handlers.empty.not_implemented)
            ],
            LINK: [
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY)), handlers.link.get),
                MessageHandler(Filters.all, handlers.empty.not_implemented)
            ],
            STATUS: [
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY)), handlers.status.get),
            ],
            CHOOSING: [
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_MANUAL_KEY)), handlers.process.next_or_stop),
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_AUTO_KEY)), handlers.category.choose_create),
                MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_NEXT_KEY)), handlers.entry.process),
                MessageHandler(Filters.all, handlers.empty.not_implemented)
            ],
            UPDATE_CATEGORY: [MessageHandler(Filters.all, handlers.category.update_)],
            GET_STATUS: [
                MessageHandler(Filters.all, handlers.status.rand),
            ],
            SET_CATEGORY: [MessageHandler(Filters.all, handlers.category.set_)],
            SET_LINK: [MessageHandler(Filters.all, handlers.link.set_)],
            RM_CATEGORY: [MessageHandler(Filters.all, handlers.category.remove)],
            RM_DOMAIN: [MessageHandler(Filters.all, handlers.domain.remove)],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), base.utils.done)],
    )