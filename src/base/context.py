from base.clients import NBotS3Client
from base.category import NBotCategoryContainer
from base.link_types import NBotLinks

from time import time
import logging

logger = logging.getLogger(__name__)


class NBotContext:
    links: list

    def __init__(self, username):
        self.username = username
        self.s3_client = NBotS3Client()
        self.categories = NBotCategoryContainer()
        self.notion_dbs = NBotLinks()
        self.connected = False

    def process(self, links):
        res = []
        for link in list(set(links).difference(set(self.links))):
            category = self.categories.search(link)
            if category:
                link = category.save_link(link)
            res.append(link)
        self.save()
        return res

    def connect(self):
        logger.info("Connecting to notion for the user {}".format(self.username))
        try:
            self.categories.connect(self.notion_dbs)
            self.connected = True
        except Exception as err:
            logger.error("Unable to connect {}".format(self.username), exc_info=True)

    def save(self):
        logger.info("{} - Saving the current state".format(self.username))
        self.s3_client.put(
            user=self.username,
            dict_value=dict(
                username=self.username,
                links=self.links,
                categories=self.categories.dump(),
                notion_links=self.notion_dbs.__dict__,
                timestamp=int(time())
            )
        )

    def load(self):
        body = self.s3_client.get(user=self.username)
        if body:
            try:
                logger.info("Loading body...")
                self.username = body['username']
                self.categories.load(body['categories'])
                self.links = body['links']
                self.notion_dbs.__dict__ = body['notion_links']
            except KeyError as err:
                logging.error("Got error!", exc_info=True)
