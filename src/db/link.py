from base.cv import NBotCV
from base.filters import empty_property
from base.constants import *

from base.utils import get_domain, MetaSingleton
from parsers.link import NBotLink
import logging

logger = logging.getLogger(__name__)


class NBotLinkDB(NBotCV):
    cv = None
    current_sync_link: str
    current_link: str
    sync_links: list

    @property
    def last_sync_link(self):
        if self.sync_links:
            self.current_sync_link = self.sync_links[0]
            return True
        return False

    @property
    def last_link(self):
        try:
            self.current_link = self.links.pop()
        except IndexError:
            return False
        return True

    def clear(self):
        logger.info("Clear the current state")
        self.current_link = ""

    def save(self, link: str, category: str, status=STATUS_TODO):
        link = NBotLink(link)
        link.soup()
        row = self.row
        row.name = link.title
        row.url = link.link
        row.domain = link.domain
        row.category = category
        row.status = status
        return row.get_browseable_url()

    def sync_domains(self):
        query = self.cv.build_query(filter=empty_property(DOMAIN_PROPERTY)).execute()
        res = []
        for row in query:
            logger.info("Updating {}".format(row.title))
            try:
                row.domain = get_domain(row.url)
                res.append(row.title)
            except Exception as err:
                logging.error(err, exc_info=True)
        return "Updated {} of {}".format(len(res), len(query))

    def sync_categories(self):
        self.sync_links = self.cv.build_query(filter=empty_property(CATEGORY_PROPERTY)).execute()
        logger.info("Got empty categories. Length: {}".format(len(self.sync_links)))
