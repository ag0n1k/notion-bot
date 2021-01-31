from notion.collection import CollectionView
from base.clients import NBotClient


class NBotCV(object):
    cv: CollectionView
    _notion_link: str

    def __init__(self):
        self.notion_client = NBotClient()

    def connect(self):
        self.cv = self.notion_client.connect(self._notion_link)

    @property
    def notion_link(self):
        return self._notion_link

    @notion_link.setter
    def notion_link(self, value):
        self._notion_link = value

    @property
    def connected(self):
        return True if self.cv else False

    @property
    def row(self):
        return self.cv.collection.add_row()
