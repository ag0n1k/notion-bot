
def get_links(message):
    if message.caption:
        entities = message.caption_entities
        text = message.caption
    else:
        entities = message.entities
        text = message.text
    return parse_links(entities=entities, text=text)


def parse_links(entities, text):
    res = set()
    for entity in entities:
        if entity.type == 'text_link':
            res.add(entity.url)
        elif entity.type == 'url':
            res.add(text[entity.offset:entity.offset + entity.length])
        else:
            print('got unknown type: ', entity.type)
    return res
