from base.constants import NOTION_LINK_TYPE
from clients.notion_db import NBotCV

import logging

logger = logging.getLogger(__name__)


class NBotLinkDB(NBotCV):
    _db_type = NOTION_LINK_TYPE

    def __init__(self):
        super().__init__()
        self._categories = {}

    def save(self, *args, **kwargs):
        pass
