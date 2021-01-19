from notion.client import NotionClient
from yc_s3 import NotionBotS3Client
from notion_helper import NotionCategory, NotionUrl
from utils import MetaSingleton
import json


class NotionBotClient(NotionClient, metaclass=MetaSingleton):
    def __init__(self, token):
        super().__init__(token_v2=token)


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
    def __init__(self, user, bot, token, chat_id):
        super(NotionContext, self).__init__(user=user, token=token)
        self.s3_client = NotionBotS3Client()
        self.bot = bot
        self.chat_id = chat_id
        self.urls = []
        self.categories = {}
        self.__load()

    def save_link(self):
        self.s3_client.put(user=self.user, value=self.link, value_type='link')

    def save_categories(self):
        self.s3_client.put(
            user=self.user,
            value=json.dumps([i.dump for i in self.categories.values()]),
            value_type='category'
        )

    def save_urls(self):
        self.s3_client.put(user=self.user, value=self.urls, value_type='urls')

    def __load(self):
        self.load_link()
        self.load_urls()
        self.load_categories()

    def load_link(self):
        body = self.s3_client.get(user=self.user, value_type='link')
        if body:
            self.link = body['value']

    def load_categories(self):
        body = self.s3_client.get(user=self.user, value_type='category')
        if body:
            for category in json.loads(body['value']):
                cat = NotionCategory()
                cat.load(category)
                self.categories.update({cat.name: cat})

    def load_urls(self):
        body = self.s3_client.get(user=self.user, value_type='links')
        if body:
            self.urls = body['value']

    def connect2notion(self):
        if self.s3_client.exists(self.user, value_type='link'):
            body = self.s3_client.get(self.user, value_type='link')
            self.link = body['value']
            self.connect()

    def get_categories(self):
        return [i for i in self.categories.keys()]

    def print_domains(self):
        if self.categories:
            self.send_message("\n".join([str(i) for i in self.categories.values()]))
        else:
            self.send_message("No categories configured")

    def send_message(self, text):
        self.bot.send_message(chat_id=self.chat_id, text=text)

    def find_category(self, domain):
        for name, cat in self.categories.items():
            if cat.search(domain):
                return cat.name
        return None

    def process(self, urls):
        res = []
        for url in list(set(urls).difference(set(self.urls))):
            n_uri = NotionUrl(url)
            cat_name = self.find_category(n_uri.domain)
            if cat_name:
                n_uri.soup()
                row = self.row
                row.name = n_uri.title
                row.url = url
                row.domain = n_uri.domain
                row.category = cat_name
                row.status = 'To Do'
                res.append(row.get_browseable_url())
            else:
                self.urls.append(url)
                res.append(url)
            del n_uri
        self.save_urls()
        self.bot.send_message(chat_id=self.chat_id, text="Processed: {}".format("\n".join(res)))

    def add_category(self, name):
        cat = NotionCategory()
        cat.name = name
        self.categories.update({name: cat})

    def update_domain(self, category, url):
        cat = self.categories.get(category, None)
        if not cat:
            self.add_category(category)
            self.update_domain(category, url)
        cat += NotionUrl(url).domain
        self.save_categories()
