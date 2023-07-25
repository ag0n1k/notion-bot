from bs4 import BeautifulSoup
import requests
from parsers.omdb import NBotOMDBParser, NBotIMDBElement, NBotIMDBSeries
import logging
import utils

logger = logging.getLogger(__name__)


class NBotLink:
    link: str
    content: BeautifulSoup = None
    domain: str
    icon = {"type": "emoji", "emoji": "📰"}
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

    def blocks(self, blocks):
        return []


class NBotWatchLink(NBotLink):
    _status = "To Do"
    icon = {"type": "emoji", "emoji": "▶️"}


class NBotCinemaLink(NBotLink):
    element: NBotIMDBElement = None
    icon = {"type": "emoji", "emoji": "🎬"}

    def process(self):
        try:
            parser = NBotOMDBParser()
            self.element = parser.get(self.link)
            if isinstance(self.element, NBotIMDBSeries):
                self.icon = {"type": "emoji", "emoji": "🍿"}
        except Exception as e:
            logger.error("Cannot parse the {}".format(self.link))
            logger.error(e, exc_info=True)

    def blocks(self, blocks):
        children = []
        if self.element is None:
            self.process()
        parser = NBotOMDBParser()
        if isinstance(self.element, NBotIMDBSeries):
            children.append({'table_of_contents': {'color': 'gray'}})
            for season in range(1, int(self.element.totalSeasons) + 1):
                s = parser.get_season(self.link, season)
                children.extend(s.to_notion())
        return children

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
