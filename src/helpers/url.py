from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


class NBotUrl(object):
    def __init__(self, url):
        self.url = url
        self.content = None

    def soup(self):
        res = requests.get(self.url)
        self.content = BeautifulSoup(res.text, 'html.parser')

    @property
    def domain(self):
        parsed_uri = urlparse(self.url)
        return parsed_uri.netloc.replace('www.', '')

    @property
    def title(self):
        if not self.soup:
            return None
        return self.content.find('title').string
