from utils import MetaSingleton
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class NBotOMDBClient(metaclass=MetaSingleton):
    url = 'http://www.omdbapi.com'
    content: Dict

    def __init__(self, api_key=None, timeout=5):
        self.key = api_key
        self.timeout = timeout
