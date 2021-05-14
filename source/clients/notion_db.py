from notion.client import NotionClient
from notion.collection import CollectionView, CollectionRowBlock, NotionDate
from utils import MetaSingleton
from typing import Dict, List
import logging

logger = logging.getLogger(__name__)


def check_attr(func):
    def wrapper(obj, attr):
        if hasattr(obj, attr):
            return func(obj, attr)
        return
    return wrapper


class NBotClient(NotionClient, metaclass=MetaSingleton):
    def __init__(self, token=None):
        super().__init__(token_v2=token)

    def connect(self, link):
        return self.get_collection_view(link)


class NBotElement:
    notion_types: Dict

    def parse(self):
        for i in list(filter(lambda x: self.notion_types[x] == 'multi_select', self.notion_types.keys())):
            self.parse_attr(i)
        for i in list(filter(lambda x: self.notion_types[x] == 'date', self.notion_types.keys())):
            self.parse_date(i)
        for i in list(filter(lambda x: self.notion_types[x] == 'number', self.notion_types.keys())):
            self.parse_number(i)

    @check_attr
    def parse_number(self, attr):
        attribute = self.__getattribute__(attr)
        try:
            self.__setattr__(attr, float(attribute))
        except ValueError:
            logger.warning("Unable to parse {} setting to 0".format(attr))
            self.__setattr__(attr, float(0))

    @check_attr
    def parse_attr(self, attr):
        attribute = self.__getattribute__(attr)
        self.__setattr__(attr, [i.strip() for i in attribute.split(',')])

    @check_attr
    def parse_date(self, attr):
        attribute = self.__getattribute__(attr)
        try:
            self.__setattr__(attr, NotionDate(datetime.strptime(attribute, '%d %b %Y').date()))
        except ValueError:
            logger.error("Unable to parse date: {}".format(attr))


class NBotCV(object):
    cv: CollectionView
    props: List
    _db_type = ""
    _notion_link = ""
    _categories: Dict[str, List[str]]

    def __init__(self):
        self.notion_client = NBotClient()

    def connect(self):
        if not self.connected:
            self.cv = self.notion_client.connect(self._notion_link)
            self.props = [prop['id'] for prop in self.cv.collection.get_schema_properties()]

    def save(self, link, status="To Do") -> str:
        raise NotImplementedError()

    def get_category_by_domain(self, domain) -> (str, None):
        for name, domains in self._categories.items():
            if domain in domains:
                return name
        return None

    def get_domains(self, category: str) -> (List, None):
        if self._categories.get(category, None):
            return self._categories[category]
        return None

    def save_item(self, item: NBotElement, row: CollectionRowBlock):
        for id_, value in item.__dict__.items():
            if id_.lower() not in self.props:
                try:
                    self.cv.collection.update_schema_properties({
                        id_.lower(): dict(name=id_.lower(), type=item.notion_types.get(id_, "text"))
                    })
                except Exception:
                    logger.error("Unable to update collection with id={}, value={}".format(id_, value), exc_info=True)
                    continue
            try:
                setattr(row, id_.lower(), value)
            except Exception:
                logger.error("Could not save {}".format(id_), exc_info=True)

    @property
    def categories(self) -> List[str]:
        return [k for k in self._categories.keys()]

    @categories.setter
    def categories(self, value: Dict[str, List[str]]):
        logger.info("Current state {} update with {}".format(self._categories, value))
        # TODO merge dicts...
        # cat = self._categories.get(value.popitem()[0], None)
        for k, v in value.items():
            current_value = self._categories.get(k, [])
            logger.info("Current state for {} is {} update {}".format(k, current_value, v))
            current_value.extend(v)
            self._categories.update({k: current_value})
        logger.info("Current state {}".format(self._categories))

    @property
    def db_type(self):
        return self._db_type

    @db_type.setter
    def db_type(self, value):
        self._db_type = value

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
    def row(self) -> CollectionRowBlock:
        return self.cv.collection.add_row()

    @property
    def json(self):
        return dict(
            link=self._notion_link,
            db_type=self._db_type,
            categories=self._categories,
        )

    @json.setter
    def json(self, body):
        self._notion_link = body['link']
        self._categories = body['categories']
        self._db_type = body['db_type']
