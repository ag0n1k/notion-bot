from notion.client import NotionClient
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


class NotionLinkDB:
    name = ""
    url = ""
    domain = ""


class NotionBotClient(object):
    def __init__(self, user, token):
        self.user = user
        self.link = None
        self.client = NotionClient(token_v2=token)
        self.cv = None

    def set_link(self, link):
        self.link = link

    def connect(self):
        self.cv = self.client.get_collection_view(self.link)

    def is_connected(self):
        return True if self.cv else False

    def add_row(self, name, url, domain):
        row = self.cv.collection.add_row()
        row.name = name
        row.url = url
        row.domain = domain
        return row.get_browseable_url()


class NotionUrl(object):
    def __init__(self, url):
        self.url = url
        self.domain = self._get_domain()
        self.content = None

    def _get_domain(self):
        parsed_uri = urlparse(self.url)
        return parsed_uri.netloc.replace('www.', '')

    def soup(self):
        res = requests.get(self.url)
        self.content = BeautifulSoup(res.text, 'html.parser')

    def get_title(self):
        if not self.soup:
            return None
        return self.content.find('title').string


class NotionContext(object):
    def __init__(self, s3_client, username, bot, token):
        self.s3_client = s3_client
        self.notion_client = NotionBotClient(username, token)
        self.username = username
        self.bot = bot
        self.chat_id = None
        self.urls = []
        self.link_domains = []
        self.load_domains()

    def set_notion_link(self, link):
        self.notion_client.set_link(link)

    def save_link(self):
        self.s3_client.put(user=self.username, value=self.notion_client.link, value_type='link')

    def save_domains(self):
        self.s3_client.put(user=self.username, value=self.link_domains, value_type='domains')

    def save_urls(self):
        self.s3_client.put(user=self.username, value=self.urls, value_type='urls')

    def load_domains(self):
        body = self.s3_client.get(user=self.username, value_type='domains')
        if body:
            self.link_domains = body['value']
        else:
            self.link_domains = []
            self.save_domains()

    def load_links(self):
        body = self.s3_client.get(user=self.username, value_type='links')
        self.urls = body['value']

    def connect2notion(self):
        if self.s3_client.exists(self.username, value_type='link'):
            body = self.s3_client.get(self.username, value_type='link')
            self.notion_client.set_link(body['value'])
            self.notion_client.connect()

    def is_connected2notion(self):
        return self.notion_client.is_connected()

    def update_domains(self, domains: list):
        self.link_domains.extend(list(set(domains).difference(set(self.link_domains))))
        self.save_domains()

    def print_domains(self, chat_id):
        self.bot.send_message(chat_id=chat_id, text="\n".join(self.link_domains))

    def process(self, urls, chat_id):
        for url in list(set(urls).difference(set(self.urls))):
            n_uri = NotionUrl(url)
            if n_uri.domain in self.link_domains:
                n_uri.soup()
                notion_url = self.notion_client.add_row(
                    name=n_uri.get_title(),
                    url=n_uri.url,
                    domain=n_uri.domain
                )
                self.bot.send_message(chat_id=chat_id, text="Created: {}".format(notion_url))
            else:
                self.urls.append(url)
            del n_uri
        self.save_urls()
