import logging

from telegram.ext import Updater


logger = logging.getLogger(__name__)


class NBot:
    updater = None
    dispatcher = None

    def __init__(self, token):
        self.updater = Updater(token, use_context=True)
        self.dispatcher = self.updater.dispatcher

    def on_error(self, update, context):
        logger.warning(f'Update "{update}" caused error "{context.error}"')

    def register_handler(self, handlers):
        for handler in handlers:
            self.dispatcher.add_handler(handler)
        self.dispatcher.add_error_handler(self.on_error)

    def start(self, *args, **kwargs):
        self.updater.start_polling(*args, **kwargs)
        self.updater.idle()
