import logging
import base.utils
import handlers.category
import handlers.entry
import handlers.link
import handlers.empty
from handlers.domain import get_domains, choose_domain, remove_domain, sync_domain
from handlers.process import next_or_stop

from helpers.constants import *

from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
    Updater
)


logger = logging.getLogger(__name__)


class NBot:
    updater = None
    dispatcher = None

    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def on_error(self, update, context):
        logger.warning(f'Update "{update}" caused error "{context.error}"')

    def register_handlers(self, handlers):
        for handler in handlers:
            self.dispatcher.add_handler(handler)
        self.dispatcher.add_error_handler(self.on_error)

    def register_conversation(self, conversation):
        self.dispatcher.add_handler(conversation)

    def start(self, *args, **kwargs):
        self.updater.start_polling(*args, **kwargs)
        self.updater.idle()


class NBotConversation:
    def __init__(self):
        self.conversation = ConversationHandler(
            entry_points=[
                CommandHandler("category", handlers.entry.category),
                CommandHandler("domain", handlers.entry.domain),
                CommandHandler("link", handlers.entry.link),
                CommandHandler("process", handlers.entry.process),
                CommandHandler("start", handlers.entry.start),
                MessageHandler(Filters.all, handlers.entry.main),
            ],
            states={
                START: [MessageHandler(Filters.all & (~Filters.command), handlers.entry.start)],
                CATEGORY: [
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY), ), handlers.category.get),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_REMOVE_KEY), ), handlers.category.choose),
                    MessageHandler(Filters.all, handlers.empty.not_implemented)
                ],
                DOMAIN: [
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY), ), get_domains),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_REMOVE_KEY), ), choose_domain),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_SYNC_KEY), ), sync_domain),
                    MessageHandler(Filters.all, handlers.empty.not_implemented)
                ],
                LINK: [
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_GET_KEY), ), handlers.link.get),
                    MessageHandler(Filters.all, handlers.empty.not_implemented)
                ],
                CHOOSING: [
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_MANUAL_KEY)), next_or_stop),
                    MessageHandler(Filters.regex('^({})$'.format(KEYBOARD_AUTO_KEY)), handlers.category.choose_create),
                    MessageHandler(Filters.all, handlers.empty.not_implemented)
                ],
                SET_CATEGORY: [MessageHandler(Filters.all, handlers.category.set)],
                SET_LINK: [MessageHandler(Filters.all, handlers.link.set)],
                RM_CATEGORY: [MessageHandler(Filters.all, handlers.category.remove)],
                RM_DOMAIN: [MessageHandler(Filters.all, remove_domain)],
            },
            fallbacks=[MessageHandler(Filters.regex('^Done$'), base.utils.done)],
        )
