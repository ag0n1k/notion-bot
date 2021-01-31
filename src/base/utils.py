from urllib.parse import urlparse
from telegram.ext import ConversationHandler


def get_domain(link):
    parsed_uri = urlparse(link)
    return parsed_uri.netloc.replace('www.', '')


def get_path(link):
    parsed_uri = urlparse(link)
    return parsed_uri.path


def check_http_in_link(link):
    if not link.startswith('http'):
        return 'http://' + link
    return link


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def done(update, context) -> int:
    update.message.reply_text("Something went wrong...")
    return ConversationHandler.END
