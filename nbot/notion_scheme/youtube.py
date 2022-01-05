from base.constants import NOTION_BUY_TYPE
from notion_scheme.decorators import notion_connect
from notion_scheme.link import NBotLink
from clients.notion_db import NBotCV, NBotCategory
import logging

logger = logging.getLogger(__name__)


class NBotYoutubeDB(NBotCV):
    _categories = {
        NBotCategory(
            name="Youtube",
            domains={
                "youtube.com",
                "youtu.be"
            },
            status="Finished"
        ),
    }

    _db_type = NOTION_BUY_TYPE

    def __init__(self):
        super().__init__()

    @notion_connect
    def save(self, link: str, status="To Do"):
        logger.info("Saving to notion: {}".format(link))
        link = NBotLink(link)
        row = self.row
        row.name = link.title
        row.url = link.link
        row.domain = link.domain
        row.status = list(self._categories)[0].status
        return row.get_browseable_url()
