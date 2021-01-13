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
        self.soup = None

    def _get_domain(self):
        parsed_uri = urlparse(self.url)
        return parsed_uri.netloc.replace('www.', '')

    def soup(self):
        res = requests.get(self.url)
        self.soup = BeautifulSoup(res.text, 'html.parser')

    def get_title(self):
        if not self.soup:
            return None
        return self.soup.find('title').string


class NotionContext(object):
    def __init__(self, s3_client, username, bot, token):
        self.s3_client = s3_client
        self.notion_client = NotionBotClient(username, token)
        self.username = username
        self.bot = bot
        self.chat_id = None
        self.link_domains = []

    def set_notion_link(self, link):
        self.notion_client.set_link(link)

    def save_link(self):
        self.s3_client.put_link(user=self.username, link=self.notion_client.link)

    def save_domains(self):
        self.s3_client.put_domains(user=self.username, domains=self.link_domains)

    def connect2notion(self):
        if self.s3_client.link_exists(self.username):
            body = self.s3_client.get_link(self.username)
            self.notion_client.set_link(body['value'])
            self.notion_client.connect()

    def is_connected2notion(self):
        return self.notion_client.is_connected()

    def process(self, url, chat_id):
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
            self.s3_client.put_url(self.username, n_uri.url)
            self.bot.send_message(chat_id=chat_id, text="Saved: {}".format(n_uri.url))

    def update_domains(self, domains: list):
        self.link_domains.extend(list(set(domains).difference(set(self.link_domains))))
        self.save_domains()

    def print_domains(self, chat_id):
        self.bot.send_message(chat_id=chat_id, text="\n".join(self.link_domains))
