from clients.notion_db import NBotCV
import logging

logger = logging.getLogger(__name__)


class NBotEmptyDB(NBotCV):
    def __init__(self, db_type):
        super().__init__()
        self._categories = []
        self._db_type = db_type

    def save(self, *args, **kwargs):
        pass
