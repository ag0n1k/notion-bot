from base.clients import NBotClient, NBotS3Client
from base.filters import *
from base.utils import get_domain
from helpers.links import NBotLink
from helpers.category import NBotCategoryContainer, NBotCategory
from helpers.constants import *
from notion.collection import CollectionView, CollectionRowBlock

from time import time
import logging
import traceback

logger = logging.getLogger(__name__)


class NBotCV(object):
    cv: CollectionView
    links: list
    sync_links: list

    def sync_domains(self):
        query = self.cv.build_query(filter=empty_property(DOMAIN_PROPERTY)).execute()
        res = []
        for row in query:
            logger.info("Updating {}".format(row.title))
            try:
                row.domain = get_domain(row.url)
                res.append(row.title)
            except Exception as err:
                logging.error(err, exc_info=True)
                traceback.print_tb(err.__traceback__)
        return "Updated {} of {}".format(len(res), len(query))

    def sync_categories(self):
        self.sync_links = self.cv.build_query(filter=empty_property(CATEGORY_PROPERTY),).execute()
        logger.info("Got empty categories. Length: {}".format(len(self.sync_links)))

    def get_all_categories_domains(self):
        res = {}
        for i in self.cv.collection.get_rows():
            cur = res.get(i.category, None)
            if not cur:
                cur = set()
            cur.add(i.domain)
            res.update({i.category: cur})
        res_ = []
        for k, v in res.items():
            res_.append("{}: {}".format(k, list(v)))
        return "\n".join(res_)

    @property
    def row(self):
        return self.cv.collection.add_row()


class NBotContext(NBotCV):
    _dblink: str
    current_sync_link: CollectionRowBlock

    def __init__(self, username):
        super().__init__()
        self.n_client = NBotClient(None)
        self.s3_client = NBotS3Client()
        self.username = username
        self.categories = NBotCategoryContainer()
        self.current_link = ""

    def connect(self):
        if self._dblink:
            self.cv = self.n_client.connect(self._dblink)

    @property
    def connected(self):
        return True if self.cv else False

    @property
    def dblink(self):
        return self._dblink

    @dblink.setter
    def dblink(self, value):
        self._dblink = value

    @property
    def last_sync_link(self):
        if self.sync_links:
            self.current_sync_link = self.sync_links[0]
            return True
        return False

    @property
    def last_link(self):
        try:
            self.current_link = self.links.pop()
        except IndexError:
            return False
        return True

    def clear(self):
        logger.info("Clear the current state")
        self.current_link = ""

    def save(self):
        logger.info("Saving the current state")
        self.s3_client.put(
            user=self.username,
            dict_value=self.__dump
        )

    def load(self):
        body = self.s3_client.get(user=self.username)
        if body:
            self.__load(body)

    def process(self, links):
        res = []
        for link in list(set(links).difference(set(self.links))):
            n_link = NBotLink(link)
            category = self.categories.search(n_link.domain)
            if category:
                res.append(self._add_row(link=n_link, category=category))
            else:
                self.links.append(link)
                res.append(link)
            del n_link
        self.save()
        return res

    def _add_row(self, link: NBotLink, category: NBotCategory, status="To Do"):
        # get the content if only the link is for auto parsing
        link.soup()
        row = self.row
        row.name = link.title
        row.url = link.link
        row.domain = link.domain
        row.category = category.name
        row.status = status
        return row.get_browseable_url()


    @property
    def __dump(self):
        return dict(
            username=self.username,
            dblink=self._dblink,
            links=self.links,
            categories=self.categories.dump(),
            timestamp=int(time())
        )

    def __load(self, body):
        logger.info(body)
        self.username = body['username']
        self.categories.load(body['categories'])
        self.dblink = body['dblink']
        self.links = body['links']
