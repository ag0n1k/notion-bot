import requests
import logging
from base.utils import MetaSingleton

logger = logging.getLogger(__name__)


class NBotIMDBClient(object, metaclass=MetaSingleton):
    url = 'http://www.omdbapi.com'

    def __init__(self, api_key, timeout=5):
        self.session = requests.Session()
        self.key = api_key
        self.timeout = timeout

    def get(self, imdb_id):
        logger.info("Getting the {}".format(imdb_id))
        res = self.session.get(self.url,
                               params=dict(
                                   apikey=self.key,
                                   i=imdb_id
                               ),
                               timeout=self.timeout)
        res.raise_for_status()
        logger.info(res)
        logger.info(res.json())
        logger.info(res.content)
        return res

