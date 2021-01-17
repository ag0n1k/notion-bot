from notion.client import NotionClient
from yc_s3 import NotionBotS3Client
from notion_helper import NotionCategory, NotionUrl, NotionRow
import json


class NotionBotClient(NotionClient):
    def __init__(self, token):
        super(NotionBotClient, self).__init__(token_v2=token)

    def __new__(cls, token):
        if not hasattr(cls, 'instance'):
            cls.instance = super(NotionBotClient, cls).__new__(cls)
        return cls.instance


class NotionCV(object):
    def __init__(self, user, token):
        self.client = NotionBotClient(token)
        self.user = user
        self._link = None
        self.cv = None

    @property
    def link(self):
        return self._link

    @link.setter
    def link(self, value):
        self._link = value

    def connect(self):
        self.cv = self.client.get_collection_view(self._link)

    @property
    def connected(self):
        return True if self.cv else False

    @property
    def row(self):
        if self.connected:
            return self.cv.collection.add_row()


class NotionContext(NotionCV):
    def __init__(self, user, bot, token):
        super(NotionContext, self).__init__(user=user, token=token)
        self.s3_client = NotionBotS3Client()
        self.bot = bot
        self.chat_id = None
        self.urls = []
        self.categories = []
        self.__load()

    def save_link(self):
        self.s3_client.put(user=self.user, value=self.link, value_type='link')

    def save_categories(self):
        self.s3_client.put(user=self.user, value=json.dumps([i.dump for i in self.categories]), value_type='category')

    def save_urls(self):
        self.s3_client.put(user=self.user, value=self.urls, value_type='urls')

    def __load(self):
        self.load_urls()
        self.load_categories()

    def load_categories(self):
        body = self.s3_client.get(user=self.user, value_type='category')
        if body:
            for category in body['value']:
                cat = NotionCategory()
                cat.load(category)
                self.categories.append(cat)

    def load_urls(self):
        body = self.s3_client.get(user=self.user, value_type='links')
        self.urls = body['value']

    def connect2notion(self):
        if self.s3_client.exists(self.user, value_type='link'):
            body = self.s3_client.get(self.user, value_type='link')
            self.link = body['value']
            self.connect()

    def print_domains(self, chat_id):
        self.bot.send_message(chat_id=chat_id, text="\n".join(self.categories))

    def process(self, urls, chat_id):
        for url in list(set(urls).difference(set(self.urls))):
            n_uri = NotionUrl(url)
            for cat in self.categories:
                if cat.search(n_uri.domain):
                    n_uri.soup()
                    row = self.row
                    row.name = n_uri.title
                    row.domain = n_uri.domain
                    row.category = cat.name
                    row.status = 'To Do'
                    self.bot.send_message(chat_id=chat_id, text="Created: {}".format(row.get_browseable_url()))
                else:
                    self.urls.append(url)
            del n_uri
        self.save_urls()
