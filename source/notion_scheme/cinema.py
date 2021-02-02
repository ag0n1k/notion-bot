from clients.notion_db import NBotCV


class NBotCinemaDB(NBotCV):
    _categories = {
        "Movie": ["m.imdb.com", "imdb.com"]
    }

    def save(self, *args, **kwargs):
        pass
