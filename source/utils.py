from urllib.parse import urlparse
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)


def get_domain(link):
    parsed_uri = urlparse(link)
    return parsed_uri.netloc.replace('www.', '')


def get_omdb_id(link):
    parsed_uri = urlparse(link)
    try:
        return list(filter(None, parsed_uri.path.split('/'))).pop()
    except IndexError:
        logger.error("Unable to get omdb id from {}".format(link), exc_info=True)
        return None


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def done(update, context) -> int:
    update.message.reply_text("Something went wrong...")
    return ConversationHandler.END
