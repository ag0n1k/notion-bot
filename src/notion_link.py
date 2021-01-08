from notion.client import NotionClient
from urllib.parse import urlparse

from bs4 import BeautifulSoup
import requests
from settings import LINK_DOMAINS


class NotionLinkDB:
    name = ""
    url = ""
    domain = ""


class NotionBotClient(object):
    def __init__(self, user):
        self.user = user
        self.token = None
        self.link = None
        self.client = None
        self.cv = None

    def set_token(self, token):
        self.token = token

    def set_link(self, link):
        self.link = link

    def connect(self):
        self.client = NotionClient(token_v2=self.token)
        self.cv = self.client.get_collection_view(self.link)

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
