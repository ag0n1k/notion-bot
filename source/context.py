from clients.s3 import NBotS3Client
from base.containers import NBotDBContainer
from time import time
import logging

logger = logging.getLogger(__name__)


class NBotContext:
    s3 = NBotS3Client(key_template="nbot_{user}_v2.json")
    buffer = dict()

    def __init__(self, username):
        self.username = username
        self.db_container = NBotDBContainer()

    def save(self):
        logger.info("{} - S3 - Saving the current state".format(self.username))
        self.s3.put(
            user=self.username,
            dict_value=dict(
                username=self.username,
                db_container=self.db_container.json,
                timestamp=int(time())
            )
        )

    def load(self):
        logger.info("{} - S3 - Load the state".format(self.username))
        body = self.s3.get(user=self.username)
        if not body:
            logger.warning("{} - S3 - No body found".format(self.username))
            return
        try:
            self.username = body['username']
            self.db_container.json = body['db_container']
        except KeyError as err:
            logger.error("Got error on load", exc_info=True)
