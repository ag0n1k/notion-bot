from base.constants import NOTION_CINEMA_TYPE
from notion_scheme.decorators import notion_connect
from clients.notion_db import NBotCV, NBotCategory
from parsers.omdb import NBotOMDBParser
import logging

logger = logging.getLogger(__name__)


class NBotCinemaDB(NBotCV):
    _categories = [
        NBotCategory(
            name="Movie",
            domains={"m.imdb.com", "imdb.com"},
            status="To Do"
        )
    ]
    _db_type = NOTION_CINEMA_TYPE

    def __init__(self):
        super().__init__()
        self._parser = NBotOMDBParser()

    @notion_connect
    def save(self, link, status="To Do", *args, **kwargs):
        row = self.row
        item = self._parser.get(link=link)
        row.url = link
        self.save_item(item=item, row=row)
        return row.get_browseable_url()
