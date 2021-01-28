import logging
from time import time
from base.clients import NBotClient, NBotS3Client

logger = logging.getLogger(__name__)


class NBotContext(object):
    def __init__(self, username):
        self.n_client = NBotClient(None)
        self.s3_client = NBotS3Client()
        self.username = username
        self._dblink = None
        self.cv = None
        self.links = list()
        self._categories = dict()

    def connect(self):
        if self._dblink:
            self.cv = self.n_client.connect(self._dblink)

    @property
    def categories(self):
        return self._categories

    @categories.setter
    def categories(self, value):
        self._categories = value

    @property
    def category_names(self):
        return [i for i in self._categories.keys()]

    @property
    def category_values(self):
        return [str(i) for i in self._categories.values()]

    def del_category(self, name):
        if self._categories.get(name, None):
            del self._categories[name]
            self.save()

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
    def __dump(self):
        return dict(
            username=self.username,
            dblink=self._dblink,
            links=self.links,
            categories=self._categories,
            timestamp=int(time())
        )

    def __load(self, body):
        logger.info(body)
        self.username = body['username']
        self.categories = body['categories']
        self.dblink = body['dblink']
        self.links = body['links']

    def save(self):
        self.s3_client.put(
            user=self.username,
            dict_value=self.__dump
        )

    def load(self):
        body = self.s3_client.get(user=self.username)
        if body:
            self.__load(body)

