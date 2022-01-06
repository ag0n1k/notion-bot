from clients.notion_db import NBotCV
from notion_scheme.buy import NBotBuyDB
from notion_scheme.youtube import NBotYoutubeDB
from notion_scheme.cinema import NBotCinemaDB
from notion_scheme.empty import NBotEmptyDB
from notion_scheme.link import NBotLinkDB
from notion_scheme.podcasts import NBotPodcastDB
from notion_scheme.read import NBotReadDB
from notion_scheme.examine import NBotExamineDB
from notion_scheme.keep import NBotKeepDB
from base.constants import NOTION_BUY_TYPE, NOTION_CINEMA_TYPE, NOTION_LINK_TYPE, NOTION_PODCAST_TYPE, \
    NOTION_YOUTUBE_TYPE, NOTION_READ_TYPE, NOTION_EXAMINE_TYPE, NOTION_KEEP_TYPE
from typing import Dict, List
import logging

from utils import get_domain

logger = logging.getLogger(__name__)


class NBotDBContainer:
    _dbs: Dict[str, NBotCV]

    def __init__(self):
        self.cinema = NBotCinemaDB()
        self.link = NBotLinkDB()
        self.podcast = NBotPodcastDB()
        self.buy = NBotBuyDB()
        self.youtube = NBotYoutubeDB()
        self.read = NBotReadDB()
        self.examine = NBotExamineDB()
        self.keep = NBotKeepDB()
        self._dbs = {
            NOTION_CINEMA_TYPE: self.cinema,
            NOTION_LINK_TYPE: self.link,
            NOTION_PODCAST_TYPE: self.podcast,
            NOTION_BUY_TYPE: self.buy,
            NOTION_YOUTUBE_TYPE: self.youtube,
            NOTION_READ_TYPE: self.read,
            NOTION_KEEP_TYPE: self.keep,
            NOTION_EXAMINE_TYPE: self.examine,
        }

    def process(self, link: str) -> (str, None):
        typ = self.get_type_by_domain(get_domain(link))
        return typ.save(link) if typ else None

    def get_type_by_domain(self, domain: str) -> (NBotCV, None):
        for item in self._dbs.values():
            if item.get_category_by_domain(domain):
                return item
        return None

    def get_type_by_category(self, category: str) -> (NBotCV, None):
        for item in self._dbs.values():
            if category in item.categories:
                return item
        return None

    def get(self, db_type: str, create_if_not_exists=False) -> NBotCV:
        if not self._dbs.get(db_type, None) and create_if_not_exists:
            self.create(db_type)
        return self._dbs.get(db_type, None)

    def create(self, db_type: str):
        self._dbs.update({db_type: NBotEmptyDB(db_type=db_type)})

    def update_categories(self, db_type: str, category: str, links: list):
        domains = [get_domain(link=link) for link in links]
        logger.info("Updating {} with {}:{}".format(db_type, category, domains))
        typ = self.get(db_type, create_if_not_exists=True)
        typ.categories = [dict(
            name=category,
            domains=domains,
            status="To Do"
        )]

    def get_categories(self):
        res = []
        for i in self._dbs.values():
            res.extend(i.categories)
        return res

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
                except KeyError:
                    logger.error("Got error on loading data for {}".format(k), exc_info=True)
