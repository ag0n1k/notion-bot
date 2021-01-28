import logging
from time import time
from base.clients import NBotClient, NBotS3Client
from helpers.links import NBotLink
from helpers.category import NBotCategoryContainer, NBotCategory
logger = logging.getLogger(__name__)


class NBotContext(object):
    def __init__(self, username):
        self.n_client = NBotClient(None)
        self.s3_client = NBotS3Client()
        self.username = username
        self._dblink = None
        self.cv = None
        self.links = list()
        self.categories = NBotCategoryContainer()
        self.current_link = ""

    def connect(self):
        if self._dblink:
            self.cv = self.n_client.connect(self._dblink)

    @property
    def connected(self):
        return True if self.cv else False

    @property
    def row(self):
        if self.connected:
            return self.cv.collection.add_row()

    @property
    def dblink(self):
        return self._dblink

    @dblink.setter
    def dblink(self, value):
        self._dblink = value

    @property
    def last_link(self):
        try:
            self.current_link = self.links.pop()
        except IndexError:
            return False
        return True

    def clear(self):
        self.current_link = ""

    def save(self):
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
