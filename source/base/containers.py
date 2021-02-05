from clients.notion_db import NBotCV
from notion_scheme.cinema import NBotCinemaDB
from notion_scheme.empty import NBotEmptyDB
from notion_scheme.link import NBotLinkDB
from base.constants import *
from typing import Dict, List
import logging

from utils import get_domain

logger = logging.getLogger(__name__)


class NBotDBContainer:
    _dbs: Dict[str, NBotCV]

    def __init__(self):
        self.cinema = NBotCinemaDB()
        self.link = NBotLinkDB()
        self._dbs = {
            NOTION_LINK_TYPE: self.link,
            NOTION_CINEMA_TYPE: self.cinema,
        }

    def process(self, link: str) -> (str, None):
        typ = self.get_type(get_domain(link))
        return typ.save(link) if typ else None

    def get_type(self, domain: str) -> (NBotCV, None):
        for item in self._dbs.values():
            if item.get_category_by_domain(domain):
                return item
        return None

    def get(self, db_type: str, create_if_not_exists=False) -> NBotCV:
        if not self._dbs.get(db_type, None) and create_if_not_exists:
            self.create(db_type)
        return self._dbs.get(db_type, None)

    def create(self, db_type: str):
        self._dbs.update({db_type: NBotEmptyDB(db_type=db_type)})

    def update_categories(self, db_type: str, category: str, domains: list):
        typ = self.get(db_type, create_if_not_exists=True)
        if isinstance(domains, str):
            domains = [domains]
        typ.categories = {category: domains}

    def remove(self, db_type):
        if self._dbs.get(db_type, None):
            del self._dbs[db_type]
        logger.info("Removed {}".format(db_type))
        logger.info(self._dbs)

    @property
    def types(self):
        return self._dbs.keys()

    @property
    def json(self):
        return [{k: t.json} for k, t in self._dbs.items()]

    @json.setter
    def json(self, body: List[Dict[str, NBotCV]]):
        for el in body:
            for k, v in el.items():
                if not self.get(k):
                    self.create(k)
                try:
                    self._dbs[k].json = v
                except KeyError as e:
                    logger.error("Got error on loading data for {}".format(k), exc_info=True)
