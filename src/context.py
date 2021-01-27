from base.clients import NotionBotClient


class NBotUser(object):
    def __init__(self, name):
        self.name = name


class NBotContext(object):
    client = None
    db = None
    links = None
    categories = None

    def __init__(self, user: NBotUser):
        self.client = NotionBotClient()
        self.user = user
        self._dblink = None
        self.cv = None
        self.links = set()
        self.categories = dict()

    @property
    def connected(self):
        return True if self.cv else False

    @property
    def row(self):
        if self.connected:
            return self.cv.collection.add_row()

    @property
    def dblink(self):
        return self._dblink

    @dblink.setter
    def dblink(self, value):
        self._dblink = value

    def save(self):
        pass

    def load(self):
        pass
