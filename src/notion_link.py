from notion.client import NotionClient
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from mechanize import Browser


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
    def __init__(self, url, parse=True):
        self.url = url
        self.domain = self.get_domain()
        self.parse = parse
        self.browser = Browser()
        self.soup = self.get_soup()
        self.title = self.soup.find('title').string

    def get_domain(self):
        parsed_uri = urlparse(self.url)
        return parsed_uri.netloc.replace('www.', '')

    def get_soup(self):
        res = self.browser.open(self.url)
        data = res.get_data()
        return BeautifulSoup(data, 'html5lib')
