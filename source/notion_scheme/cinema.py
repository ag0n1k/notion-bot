from base.constants import NOTION_CINEMA_TYPE
from notion_scheme.decorators import notion_connect
from clients.notion_db import NBotCV


class NBotCinemaDB(NBotCV):
    _categories = {
        "Movie": ["m.imdb.com", "imdb.com"]
    }
    _db_type = NOTION_CINEMA_TYPE

    @notion_connect
    def save(self, link, status="To Do", *args, **kwargs):
        pass
