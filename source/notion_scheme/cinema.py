from base.constants import NOTION_CINEMA_TYPE
from clients.notion_db import NBotCV


class NBotCinemaDB(NBotCV):
    _categories = {
        "Movie": ["m.imdb.com", "imdb.com"]
    }
    _db_type = NOTION_CINEMA_TYPE

    def save(self, *args, **kwargs):
        pass
