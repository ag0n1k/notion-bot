from clients.notion_db import NBotClient
import json
import logging
import os

from typing import Dict

logger = logging.getLogger(__name__)


class NBotData:
    link = "https://www.notion.so/c293f550fc2d4ca6bb8e5425c5fb280d?v=dccd59846ef045119b773fa9b0d558b3"
    data = dict()
    notion_client = NBotClient(token=os.environ.get('NOTION_TOKEN'))

    def __init__(self):
        self.cv = self.notion_client.connect(self.link)
        for row in self.cv.collection.query():
            self.update(row.title, row)

    def update(self, key, value):
        self.data.update({key: value})

    def create(self, user):
        row = self.cv.collection.add_row()
        row.title = user
        row.data = "{}"
        self.update(user, row)
        return row

    def put(self, user, dict_value):
        row = self.get_row(user)
        row.data = json.dumps(dict_value)

    def get(self, user) -> Dict[str, str]:
        row = self.get_row(user)
        return json.loads(row.data)

    def get_row(self, user):
        row = self.data.get(user, None)
        if not row:
            row = self.create(user)
        return row

