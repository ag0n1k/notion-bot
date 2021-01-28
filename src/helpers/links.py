from base.utils import get_domain
from bs4 import BeautifulSoup
import requests


class NBotLink(object):
    def __init__(self, link):
        self.link = link
        self.content = None

    def soup(self):
        res = requests.get(self.link)
        self.content = BeautifulSoup(res.text, 'html.parser')

    @property
    def domain(self):
        return get_domain(self.link)

    @property
    def title(self):
        if not self.soup:
            return None
        return self.content.find('title').string
