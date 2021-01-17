from notion.client import NotionClient
from yc_s3 import NotionBotS3Client


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

    def add_row(self, name, url, domain):
        row = self.cv.collection.add_row()
        row.name = name
        row.url = url
        row.domain = domain
        return row.get_browseable_url()


class NotionContext(NotionCV):
    def __init__(self, user, bot, token):
        super(NotionContext, self).__init__(user=user, token=token)
        self.s3_client = NotionBotS3Client()
        self.bot = bot
        self.chat_id = None
        self.urls = []
        self.link_domains = []
        self.load_domains()

    def save_link(self):
        self.s3_client.put(user=self.user, value=self.link, value_type='link')

    def save_domains(self):
        self.s3_client.put(user=self.user, value=self.link_domains, value_type='domains')

    def save_urls(self):
        self.s3_client.put(user=self.user, value=self.urls, value_type='urls')

    def load_domains(self):
        body = self.s3_client.get(user=self.user, value_type='domains')
        if body:
            self.link_domains = body['value']
        else:
            self.link_domains = []
            self.save_domains()

    def load_links(self):
        body = self.s3_client.get(user=self.user, value_type='links')
        self.urls = body['value']

    def connect2notion(self):
        if self.s3_client.exists(self.user, value_type='link'):
            body = self.s3_client.get(self.user, value_type='link')
            self.link = body['value']
            self.connect()

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
                notion_url = self.add_row(
                    name=n_uri.get_title(),
                    url=n_uri.url,
                    domain=n_uri.domain
                )
                self.bot.send_message(chat_id=chat_id, text="Created: {}".format(notion_url))
            else:
                self.urls.append(url)
            del n_uri
        self.save_urls()
