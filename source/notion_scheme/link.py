from base.constants import NOTION_LINK_TYPE
from bs4 import BeautifulSoup
from clients.notion_db import NBotCV
import requests
import logging

from utils import get_domain

logger = logging.getLogger(__name__)


def ensure_http_in_link(link):
    if not link.startswith('http'):
        return 'http://' + link
    return link


class NBotLink:
    link: str
    content: BeautifulSoup

    def __init__(self, link):
        self.link = ensure_http_in_link(link)
        res = requests.get(self.link)
        self.content = BeautifulSoup(res.text, 'html.parser')

    @property
    def title(self):
        if not self.content:
            return None
        return self.content.find('title').string

    @property
    def domain(self):
        return get_domain(self.link)


class NBotLinkDB(NBotCV):
    _db_type = NOTION_LINK_TYPE

    def __init__(self):
        super().__init__()
        self._categories = {}

    def save(self, link, status="To Do"):
        link = NBotLink(link)
        row = self.row
        row.name = link.title
        row.url = link.link
        row.domain = link.domain
        row.category = self.get_category_by_domain(link.domain)
        row.status = status
        return row.get_browseable_url()
