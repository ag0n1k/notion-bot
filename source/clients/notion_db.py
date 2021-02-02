from notion.client import NotionClient
from notion.collection import CollectionView
from utils import MetaSingleton
from typing import Dict, List


class NBotClient(NotionClient, metaclass=MetaSingleton):
    def __init__(self, token=None):
        super().__init__(token_v2=token)

    def connect(self, link):
        return self.get_collection_view(link)


class NBotCV(object):
    cv: CollectionView
    _notion_link = ""
    _categories: Dict[str, List[str]]

    def __init__(self):
        self.notion_client = NBotClient()

    def connect(self):
        self.cv = self.notion_client.connect(self._notion_link)

    def save(self, *args, **kwargs):
        raise NotImplementedError()

    @property
    def categories(self) -> Dict[str, List[str]]:
        return self._categories

    @categories.setter
    def categories(self, value: Dict[str, List[str]]):
        # TODO merge dicts...
        # cat = self._categories.get(value.popitem()[0], None)
        self._categories.update(value)

    @property
    def notion_link(self):
        return self._notion_link

    @notion_link.setter
    def notion_link(self, value):
        self._notion_link = value

    @property
    def connected(self):
        return hasattr(self, 'cv')

    @property
    def row(self):
        return self.cv.collection.add_row()

    @property
    def json(self):
        return dict(link=self._notion_link)

    @json.setter
    def json(self, body):
        self._notion_link = body['link']
