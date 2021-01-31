from base.context import NBotCV
from db.filters import empty_property
from base.constants import *
import logging

from base.utils import get_domain
from parsers.link import NBotLink

logger = logging.getLogger(__name__)


class NBotLinkDB(NBotCV):
    cv = None

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

    def process(self, links):
        res = []
        for link in list(set(links).difference(set(self.links))):
            n_link = NBotLink(link)
            category = self.categories.search(n_link.domain)
            if category:
                logger.info("Saving {} to notion".format(link))
                res.append(self._add_row(link=n_link, category=category))
            else:
                logger.info("Saving {} for process".format(link))
                self.links.append(link)
                res.append(link)
            del n_link
        self.save()
        return res

    def _add_row(self, link: NBotLink, category: NBotCategory, status=STATUS_TODO):
        # get the content if only the link is for auto parsing
        link.soup()
        row = self.row
        row.name = link.title
        row.url = link.link
        row.domain = link.domain
        row.category = category.name
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
