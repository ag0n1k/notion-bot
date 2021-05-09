from base.containers import NBotDBContainer
from clients.notion_db import NBotCV
from clients.notion_data import NBotData
# from clients.s3 import NBotS3Client
from time import time
import logging

logger = logging.getLogger(__name__)


class NBotContext:
    # storage = NBotS3Client(key_template="nbot_{user}_v2.json")
    storage = NBotData()
    cv_buffer: NBotCV
    link_buffer: str
    category_buffer: str

    def __init__(self, username):
        self.username = username
        self.db_container = NBotDBContainer()
        self.store = []

    def store_difference(self, links):
        return list(set(links).difference(set(self.store)))

    def save(self):
        logger.info("{} - storage - Saving the current state".format(self.username))
        self.storage.put(
            user=self.username,
            dict_value=dict(
                username=self.username,
                db_container=self.db_container.json,
                store=self.store,
                timestamp=int(time())
            )
        )

    def load(self):
        logger.info("{} - storage - Load the state".format(self.username))
        body = self.storage.get(user=self.username)
        if not body:
            logger.warning("{} - storage - No body found".format(self.username))
            return
        try:
            logger.info("{} - storage - Got body {}".format(self.username, body))
            self.username = body['username']
            self.db_container.json = body['db_container']
            self.store = body['store']
        except KeyError as err:
            logger.error("Got error on load", exc_info=True)
