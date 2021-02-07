from base.constants import NOTION_CINEMA_TYPE
from notion_scheme.decorators import notion_connect
from clients.notion_db import NBotCV
from parsers.omdb import NBotOMDBParser
import logging

logger = logging.getLogger(__name__)


class NBotCinemaDB(NBotCV):
    _categories = {
        "Movie": ["m.imdb.com", "imdb.com"]
    }
    _db_type = NOTION_CINEMA_TYPE

    def __init__(self):
        super().__init__()
        self._parser = NBotOMDBParser()

    @notion_connect
    def save(self, link, status="To Do", *args, **kwargs):
        row = self.row
        item = self._parser.get(link=link)
        for id_, value in item.__dict__.items():
            if id_.lower() not in [prop['id'] for prop in self.cv.collection.get_schema_properties()]:
                try:
                    self.cv.collection.update_schema_properties({
                        id_.lower(): dict(name=id_.lower(), type=item.notion_types.get(id_, "text"))
                    })
                except Exception:
                    logger.error("Unable to update collection with id={}, value={}".format(id_, value), exc_info=True)
                    continue
            if isinstance(value, list):
                value = value.pop()
            else:
                value = str(value)
            try:
                setattr(row, id_.lower(), value)
            except Exception:
                logger.error("Could not save {}".format(id_), exc_info=True)
        return row.get_browseable_url()
