import logging
from notion_client import Client

from utils import MetaSingleton

logger = logging.getLogger(__name__)


class NBotClient(metaclass=MetaSingleton):
    _domain_map = {}
    _db_map = {}

    def __init__(self, token=None):
        self.client = Client(auth=token)
        self.init_maps()

    def init_maps(self):
        logger.info("Initializing the current state...")
        for db in self.client.databases.list()['results']:
            for domain in [opt['name'] for opt in db['properties']['Domain']['select']['options']]:
                self._domain_map[domain] = db['id']
            self._db_map[db['title'][0]['text']['content']] = db['id']
        logger.info("Initializing complete: "
                    "domains={domains}, databases={databases}.".format(domains=len(self._domain_map),
                                                                       databases=len(self._db_map)))

    def update_domains(self):
        # todo: from notion https://www.notion.so/ag0n1k/NBot-Update-domains-8587d38145794434948c94710ae3eed8
        pass

    def get_id_by_domain(self, domain) -> [str, None]:
        if domain not in self._domain_map.keys():
            return None
        else:
            return self._domain_map[domain]

    @property
    def databases(self):
        return list(self._db_map.keys())

    def get_id_by_db_name(self, name):
        if name not in self._db_map.keys():
            return None
        else:
            return self._db_map[name]

    def create_page(self, database_id, props):
        logger.info(f"Saving to {database_id}")
        page = self.client.pages.create(parent={"database_id": database_id}, properties=props, children=[])
        return page['url']
