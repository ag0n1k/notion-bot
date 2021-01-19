class TelegramMessageUrl(object):
    def __init__(self, message):
        self.message = message
        self.urls = set()

    def parse_urls(self):
        if self.message.caption:
            self._parse_urls(entities=self.message.caption_entities, text=self.message.caption)
        else:
            self._parse_urls(entities=self.message.entities, text=self.message.text)

    def _parse_urls(self, entities, text):
        for entity in entities:
            if entity.type == 'text_link':
                self.urls.add(entity.url)
            elif entity.type == 'url':
                self.urls.add(text[entity.offset:entity.offset + entity.length])
            else:
                print('got unknown type: ', entity.type)

