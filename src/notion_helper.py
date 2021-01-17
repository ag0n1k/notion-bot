from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests, json


class NotionCategory(object):
    def __init__(self):
        self._name = None
        self._domains = []

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def domains(self):
        return self._domains

    def __add__(self, other):
        self._domains.append(other)

    def search(self, domain: str):
        return self._name if domain in self._domains else None

    def dump(self):
        return json.dumps({
            self._name: self._domains
        })

    def load(self, body):
        res = json.loads(body)
        self._name = res['name']
        self._domains = res['domains']


class NotionUrl(object):
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
