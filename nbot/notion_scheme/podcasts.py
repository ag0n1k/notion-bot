from base.constants import NOTION_PODCAST_TYPE
from notion_scheme.decorators import notion_connect
from notion_scheme.link import NBotLink
from clients.notion_db import NBotCV, NBotElement, NBotCategory
import logging

logger = logging.getLogger(__name__)


class NBotPodcastElement(NBotElement):
    url: str
    domain: str
    status: str
    date: str

    notion_types = dict(
        url="url",
        domain="select",
        status="select",
        date="date",
    )


class NBotPodcastDB(NBotCV):
    _categories = {
        NBotCategory(
            name="Podcasts",
            domains={"podcasts.google.com", "podcasts.apple.com", "music.yandex.ru"},
            status="Listening"
        )
    }
    _db_type = NOTION_PODCAST_TYPE

    def __init__(self):
        super().__init__()

    @notion_connect
    def save(self, link, status="Listening", *args, **kwargs):
        link = NBotLink(link)
        row = self.row
        item = NBotPodcastElement()
        row.name = link.title
        item.url = link.link
        item.domain = link.domain
        item.status = status
        self.save_item(item=item, row=row)
        return row.get_browseable_url()
