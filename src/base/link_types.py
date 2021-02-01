from base.constants import *
from db.cinema import NBotCinemaDB
from db.link import NBotLinkDB


class NBotLinks:
    cinema: str
    link: str
    DB_TYPES_IMPLEMENTATION = {
        LINK_TYPE: NBotLinkDB,
        CINEMA_TYPE: NBotCinemaDB
    }

    @property
    def connected(self):
        if hasattr(self, 'cinema') and hasattr(self, 'link'):
            return True
        return False
