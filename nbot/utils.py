from urllib.parse import urlparse
from aiogram import types
import logging
from typing import List

logger = logging.getLogger(__name__)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def ensure_http_in_link(link):
    if not link.startswith('http'):
        return 'http://' + link
    return link


def domain(link):
    parsed_uri = urlparse(link)
    return parsed_uri.netloc.replace('www.', '')


def parse_links(entities: List[types.MessageEntity], text: str):
    res = set()
    for entity in entities:
        if entity.type == 'text_link':
            res.add(entity.url)
        elif entity.type == 'url':
            res.add(text[entity.offset:entity.offset + entity.length])
        else:
            logger.warning('got unknown type: {}'.format(entity.type))
    return res


class MetaSingleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
