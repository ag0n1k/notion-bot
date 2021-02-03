from clients.notion_db import NBotCV
from notion_scheme.cinema import NBotCinemaDB
from notion_scheme.empty import NBotEmptyDB
from notion_scheme.link import NBotLinkDB
from base.constants import *
from typing import Dict, List


class NBotDBContainer:
    _dbs: Dict[str, NBotCV]

    def __init__(self):
        self.cinema = NBotCinemaDB()
        self.link = NBotLinkDB()
        self._dbs = {
            NOTION_LINK_TYPE: self.link,
            NOTION_CINEMA_TYPE: self.cinema,
        }

    def get(self, db_type: str, create_if_not_exists=False) -> NBotCV:
        if not self._dbs.get(db_type, None) and create_if_not_exists:
            self.create(db_type)
        return self._dbs.get(db_type, None)

    def create(self, db_type: str):
        self._dbs.update({db_type: NBotEmptyDB()})

    @property
    def types(self):
        return self._dbs.keys()

    @property
    def json(self):
        return [{k: t.json} for k, t in self._dbs.items()]

    @json.setter
    def json(self, body: List[Dict[str, NBotCV]]):
        for el in body:
            for k, v in el:
                if not self.get(k):
                    self.create(k)
                self._dbs[k].json = v
