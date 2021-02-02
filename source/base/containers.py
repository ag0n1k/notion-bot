from clients.notion_db import NBotCV
from notion_scheme.cinema import NBotCinemaDB
from notion_scheme.link import NBotLinkDB
from base.constants import *
from typing import Dict, List


class NBotDBContainer:
    def __init__(self):
        self.cinema = NBotCinemaDB()
        self.link = NBotLinkDB()
        self.type_map = {
            NOTION_LINK_TYPE: self.link,
            NOTION_CINEMA_TYPE: self.cinema,
        }

    def get(self, name: str) -> NBotCV:
        return self.type_map[name]

    @property
    def json(self):
        return [{k: t.json} for k, t in self.type_map.items()]

    @json.setter
    def json(self, body: List[Dict[str, NBotCV]]):
        for el in body:
            for k, v in el:
                self.type_map[k].json = v
