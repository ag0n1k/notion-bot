from base.clients import NBotS3Client
from base.category import NBotCategoryContainer

from time import time
import logging

logger = logging.getLogger(__name__)


class NBotContext:
    def __init__(self, username):
        self.s3_client = NBotS3Client()
        self.username = username
        self.categories = NBotCategoryContainer()
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
            try:
                self.__load(body)
            except KeyError as err:
                logging.error("Got error on load", exc_info=True)

    @property
    def __dump(self):
        return dict(
            username=self.username,
            dblink=self._dblink,
            links=self.links,
            categories=self.categories.dump(),
            statuses=self.statuses,
            timestamp=int(time())
        )

    def __load(self, body):
        logger.info(body)
        self.username = body['username']
        self.categories.load(body['categories'])
        self.dblink = body['dblink']
        self.links = body['links']
        self.statuses = body['statuses']
