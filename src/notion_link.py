from notion.client import NotionClient


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

    def add_row(self, name, url, domain):
        row = self.cv.collection.add_row()
        row.name = name
        row.url = url
        row.domain = domain
        return row.get_browseable_url()

