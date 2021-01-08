from notion.client import NotionClient
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests
from settings import LINK_DOMAINS


def connect(token, link):
    return NotionBotClient(token=token, link=link)


class NotionLinkDB:
    name = ""
    url = ""
    domain = ""


class NotionBotClient(object):
    def __init__(self, token, link):
        self.token = token
        self.link = link
        self.client = self.connect()
        self.cv = self.get_collection_view()

    def connect(self):
        return NotionClient(token_v2=self.token)

    def get_collection_view(self):
        return self.client.get_collection_view(self.link)

    def add_row(self, name, url, domain):
        row = self.cv.collection.add_row()
        row.name = name
        row.url = url
        row.domain = domain
        return row.get_browseable_url()


class NotionUrl(object):
    link_domain = (
        'youtube.com',
        'twitch.com',
    )

    def __init__(self, url, force_link=False):
        self.url = url
        self.parse = self.link_or_content(force=force_link)
        self.soup = self.get_soup()

    def link_or_content(self, force):
        domain = self.get_domain()
        if domain in LINK_DOMAINS or force:
            return True
        return False

    def get_domain(self):
        parsed_uri = urlparse(self.url)
        return parsed_uri.netloc.replace('www.', '')

    def get_soup(self):
        if self.parse:
            res = requests.get(self.url)
            soup = BeautifulSoup(res.text, 'html.parser')
            return soup
        return None

    def get_title(self):
        if not self.soup:
            return None
        return self.soup.find('title').string
