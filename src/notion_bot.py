from notion.client import NotionClient
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import requests


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
    def __init__(self, s3_client, username, bot):
        self.s3_client = s3_client
        self.notion_client = NotionBotClient(username)
        self.username = username
        self.bot = bot
        self.chat_id = None
        self.link_domains = []

    def set_notion_link(self, link):
        self.notion_client.set_link(link)

    def set_notion_token(self, token):
        self.notion_client.set_token(token)

    def save_token(self):
        self.s3_client.put_token(user=self.username, link=self.notion_client.link, token=self.notion_client.token)

    def save_domains(self):
        self.s3_client.put_domains(user=self.username, domains=self.link_domains)

    def connect2notion(self):
        if self.s3_client.token_exists(self.username):
            body = self.s3_client.get_token(self.username)
            self.notion_client.set_link(body['value']['link'])
            self.notion_client.set_token(body['value']['token'])
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

    def update_domains(self, domain):
        if domain not in set(self.link_domains):
            self.link_domains.append(domain)
            self.save_domains()
