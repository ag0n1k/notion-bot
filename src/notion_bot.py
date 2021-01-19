from notion.client import NotionClient
from yc_s3 import NotionBotS3Client
from notion_helper import NotionCategory, NotionUrl
from utils import MetaSingleton
import json

import logging


class NotionBotClient(NotionClient, metaclass=MetaSingleton):
    def __init__(self, token):
        super().__init__(token_v2=token)


class NotionCV(object):
    def __init__(self, user, token):
        self.client = NotionBotClient(token)
        self.log = logging.getLogger("NotionBot")
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
        self.log.info("Saving the link for the user: {user}".format(user=self.user))
        self.s3_client.put(user=self.user, value=self.link, value_type='link')

    def save_categories(self):
        self.log.info(
            "Saving the categories for the user: {user}, "
            "categories: {cat}".format(user=self.user, cat=self.categories.values())
        )
        self.s3_client.put(
            user=self.user,
            value=json.dumps([i.dump for i in self.categories.values()]),
            value_type='category'
        )

    def save_urls(self):
        self.log.info("Saving the urls for the user: {user}, urls: {urls}".format(user=self.user, urls=self.urls))
        self.s3_client.put(user=self.user, value=self.urls, value_type='urls')

    def __load(self):
        self.load_link()
        self.load_urls()
        self.load_categories()

    def load_link(self):
        self.log.info("Loading the link for the user: {user}".format(user=self.user))
        body = self.s3_client.get(user=self.user, value_type='link')
        if body:
            self.log.info("Found the link for the user: {user}".format(user=self.user))
            self.link = body['value']

    def load_categories(self):
        self.log.info("Loading the categories for the user: {user}".format(user=self.user))
        body = self.s3_client.get(user=self.user, value_type='category')
        if body:
            self.log.info("Found the categories for the user: {user}".format(user=self.user))
            for category in json.loads(body['value']):
                cat = NotionCategory()
                cat.load(category)
                self.categories.update({cat.name: cat})
            self.log.info("Load categories finished for the user: {user}.".format(user=self.user))

    def load_urls(self):
        self.log.info("Loading the urls for the user: {user}".format(user=self.user))
        body = self.s3_client.get(user=self.user, value_type='urls')
        if body:
            self.log.info("Found the urls for the user: {user}".format(user=self.user))
            self.urls = body['value']

    def connect2notion(self):
        self.log.info("Connecting to notion for the user: {user}".format(user=self.user))
        if self.s3_client.exists(self.user, value_type='link'):
            body = self.s3_client.get(self.user, value_type='link')
            self.link = body['value']
            self.connect()
            self.log.info("Connection to notion established for the user: {user}".format(user=self.user))

    def get_categories(self):
        self.log.info("Sending the categories back for the user: {user}".format(user=self.user))
        return [i for i in self.categories.keys()]

    def print_domains(self):
        self.log.info("Sending the categories back for the user: {user}".format(user=self.user))
        if self.categories:
            self.send_message("\n".join([str(i) for i in self.categories.values()]))
        else:
            self.send_message("No categories configured")

    def send_message(self, text):
        self.log.info("Sending the message for the user: {user}, {message}".format(user=self.user, message=text))
        self.bot.send_message(chat_id=self.chat_id, text=text)

    def find_category(self, domain):
        self.log.info("Searching the domain for the user {user}, {domain}".format(user=self.user, domain=domain))
        for name, cat in self.categories.items():
            if cat.search(domain):
                self.log.info("Category for the user {user} was found: {cat}".format(user=self.user, cat=cat.name))
                return cat.name
        self.log.info("No category for the user {user} was found".format(user=self.user))
        return None

    def process(self, urls):
        self.log.info("Processing the urls for the user {user}, {urls}".format(user=self.user, urls=urls))
        res = []
        for url in list(set(urls).difference(set(self.urls))):
            self.log.info("Processing the url for the user {user}, {url}".format(user=self.user, url=url))
            n_uri = NotionUrl(url)
            cat_name = self.find_category(n_uri.domain)
            self.log.info("Category for the url for the user {user}, {cat}".format(user=self.user, cat=cat_name))
            if cat_name:
                n_uri.soup()
                row = self.row
                row.name = n_uri.title
                row.url = url
                row.domain = n_uri.domain
                row.category = cat_name
                row.status = 'To Do'
                res.append(row.get_browseable_url())
                self.log.info("Saved the url for the user {user} to notion {notion}".format(
                    user=self.user, notion=row.get_browseable_url()))
            else:
                self.urls.append(url)
                res.append(url)
            del n_uri
        self.save_urls()
        self.bot.send_message(chat_id=self.chat_id, text="Processed: {}".format("\n".join(res)))

    def add_category(self, name):
        self.log.info("Adding the category for the user {user}, {cat}".format(user=self.user, cat=name))
        cat = NotionCategory()
        cat.name = name
        self.categories.update({name: cat})

    def remove_category(self, name):
        if self.categories.get(name, None):
            self.log.info("Removing the category for the user {user}, {cat}".format(user=self.user, cat=name))
            del self.categories[name]
            self.save_categories()
            self.bot.send_message(chat_id=self.chat_id, text="Category removed: {}".format(name))

    def update_domain(self, category, url):
        self.log.info("Updating the category for the user {user}, {cat} with {url}".format(
            user=self.user, cat=category, url=url))
        cat = self.categories.get(category, None)
        if not cat:
            self.log.info("Category for the user {user}, not found: {cat}".format(user=self.user, cat=cat))
            self.add_category(category)
            self.update_domain(category, url)
        cat += NotionUrl(url).domain
        self.save_categories()
