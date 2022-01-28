import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)


def check_attr(func):
    def wrapper(obj, attr):
        if hasattr(obj, attr):
            return func(obj, attr)
        return
    return wrapper


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
            self.__setattr__(attr, datetime.strptime(attribute, '%d %b %Y').date().isoformat())
        except ValueError:
            logger.error("Unable to parse date: {}".format(attr))
            self.__setattr__(attr, None)
