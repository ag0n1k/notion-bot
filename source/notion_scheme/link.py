from clients.notion_db import NBotCV
import logging

logger = logging.getLogger(__name__)


class NBotLinkDB(NBotCV):
    def save(self, *args, **kwargs):
        pass
