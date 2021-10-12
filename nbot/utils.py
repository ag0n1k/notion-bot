from urllib.parse import urlparse

from telegram import InlineKeyboardButton
import logging

logger = logging.getLogger(__name__)


def get_domain(link):
    parsed_uri = urlparse(link)
    return parsed_uri.netloc.replace('www.', '')


def get_first_path(link):
    parsed_uri = urlparse(link)
    if parsed_uri.path:
        return parsed_uri.path.split('/')[1]
    else:
        return ''


def get_omdb_id(link):
    parsed_uri = urlparse(link)
    try:
        return list(filter(None, parsed_uri.path.split('/'))).pop()
    except IndexError:
        logger.error("Unable to get omdb id from {}".format(link), exc_info=True)
        return None


def create_buttons(_list: list, _length=3):
    res = []
    tmp = []
    for i, t in enumerate(_list):
        if (i + 1) % _length == 0:
            res.append(tmp)
            tmp = []
        tmp.append(InlineKeyboardButton(text=t, callback_data=t))
    res.append(tmp)
    return res


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
