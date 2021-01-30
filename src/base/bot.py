import logging
import base.utils
from handlers.category import (
    choose_category,
    get_categories,
    remove_category,
    set_category,
    choose_or_create_category
)
from handlers.start import set_link, handler_start
from handlers.empty import not_implemented
from handlers.entry import category, domain, link, main, process
from handlers.domain import get_domains, choose_domain, remove_domain, sync_domain
from handlers.process import next_or_stop
from handlers.link import get_links

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
            fallbacks=[MessageHandler(Filters.regex('^Done$'), base.utils.done)],
        )
