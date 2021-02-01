from base.clients import NBotOMDBClient
from base.cv import NBotCV
from base.constants import *


class NBotCinemaDB(NBotOMDBClient, NBotCV):

    def save(self, link: str, category: str, status='To Do'):
        row = self.row
        row.name = link
        row.url = link
        row.category = category
        row.status = status
        return row.get_browseable_url()
