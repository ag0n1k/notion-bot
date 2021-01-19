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

    @domains.setter
    def domains(self, value):
        self._domains = value

    def __add__(self, other):
        if not isinstance(other, list):
            other = [other]
        self._domains.extend(list(set(other).difference(set(self.domains))))

    def search(self, domain: str):
        return self._name if domain in self._domains else None

    def __str__(self):
        return "{}: {}".format(self._name, self.domains)

    @property
    def dump(self):
        return {
            'name': self._name,
            'domains': self._domains
        }

    def load(self, body: dict):
        self.name = body['name']
        self.domains = body['domains']


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
