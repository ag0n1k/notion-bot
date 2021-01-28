from base.clients import NBotClient, NBotS3Client
import json


class NBotUser(object):
    def __init__(self, name):
        self.name = name


class NBotContext(object):
    client = None
    db = None
    links = None
    categories = None

    def __init__(self, user: NBotUser):
        self.n_client = NBotClient(None)
        self.s3_client = NBotS3Client()
        self.user = user
        self._dblink = None
        self.cv = None
        self.links = list()
        self.categories = dict()

    def connect(self):
        if self._dblink:
            self.cv = self.n_client.connect(self._dblink)

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

    @property
    def __dump(self):
        return dict(
            user=self.user,
            dblink=self._dblink,
            links=self.links,
            categories=self.categories
        )

    def save(self):
        self.s3_client.put(
            user=self.user,
            value=json.dumps(self.__dump)
        )

    def load(self):
        pass
