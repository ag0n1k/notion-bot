from bs4 import BeautifulSoup
import requests
from parsers.omdb import NBotOMDBParser, NBotIMDBElement
import logging
import utils

logger = logging.getLogger(__name__)


class NBotLink:
    link: str
    content: BeautifulSoup = None
    domain: str
    _status = "To Do"
    _domains = set()

    def __init__(self, link):
        self.link = utils.ensure_http_in_link(link)
        self.domain = utils.domain(link)

    def process(self):
        try:
            res = requests.get(self.link)
            self.content = BeautifulSoup(res.text, 'html.parser')
        except Exception as e:
            logger.error("Cannot parse the {}".format(self.link))
            logger.error(e, exc_info=True)

    @property
    def title(self):
        try:
            if not self.content:
                return "No Content, Sorry"
            return self.content.find('title').string
        except AttributeError:
            return "No Title, Sorry"

    @property
    def properties(self):
        return {
            "Name": {"title": [{"text": {"content": self.title}}]},
            "Status": {"select": {"name": self._status}},
            "Domain": {"select": {"name": self.domain}},
            "URL": {"type": "url", "url": self.link},
        }


class NBotWatchLink(NBotLink):
    _status = "Finished"


class NBotCinemaLink(NBotLink):
    element: NBotIMDBElement

    def process(self):
        parser = NBotOMDBParser()
        try:
            self.element = parser.get(self.link)
        except Exception as e:
            logger.error("Cannot parse the {}".format(self.link))
            logger.error(e, exc_info=True)

    @property
    def properties(self):
        default_ = {
            "URL": {"type": "url", "url": self.link},
            "Domain": {"select": {"name": self.domain}},
        }
        if not self.element:
            return default_.update({"Name": {"title": [{"text": {"content": "Not Parsed"}}]}})
        props = self.element.dict()
        props.update(default_)
        return props
