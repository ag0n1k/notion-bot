from clients.notion_db import NBotCV
import logging

logger = logging.getLogger(__name__)


def notion_connect(func):
    def wrapper(obj: NBotCV, *args, **kwargs):
        if not obj.connected:
            logger.info("Connecting to notion type {}".format(obj.db_type))
            obj.connect()
        return func(obj, *args, **kwargs)
    return wrapper
