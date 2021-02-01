from clients import NBotS3Client
from time import time
import logging

logger = logging.getLogger(__name__)


class NBotContext:
    s3 = NBotS3Client(key_template="nbot_{user}_v2.json")
    start_over = False

    def __init__(self, username):
        self.username = username

    def save(self):
        logger.info("{} - S3 - Saving the current state".format(self.username))
        self.s3.put(
            user=self.username,
            dict_value=dict(
                username=self.username,
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
        except KeyError as err:
            logger.error("Got error on load", exc_info=True)
