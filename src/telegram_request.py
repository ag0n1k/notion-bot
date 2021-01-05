from telegram.ext import Updater
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, Filters
from notion_link import NotionBotClient, NotionUrl
from settings import NOTION_TOKEN, NOTION_DB, TGRAM_TOKEN

updater = Updater(token=TGRAM_TOKEN, use_context=True)

dispatcher = updater.dispatcher
client = NotionBotClient(token=NOTION_TOKEN, link=NOTION_DB)


def start(update, context):
    print(context)
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")


def echo(update, context):
    print(update.message)
    print(context.args)
    print(context.__dict__)
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


def parse_url(text: str, entities: list):
    result = set()
    for entity in entities:
        if entity.type == 'text_link':
            result.add(NotionUrl(entity.url))
        elif entity.type == 'url':
            result.add(NotionUrl(text[entity.offset:entity.offset+entity.length]))
        else:
            print('got unknown type: ', entity.type)
    return list(result)


def test(update, context):
    res = list()
    print(update.message)
    if update.message.text:
        res = parse_url(update.message.text, update.message.entities)
    elif update.message.caption:
        res = parse_url(update.message.caption, update.message.caption_entities)
    for i in res:
        notion_url = client.add_row(name=i.title, url=i.url, domain=i.domain)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Created: {}".format(notion_url))


start_handler = CommandHandler('start', start)
dispatcher.add_handler(start_handler)

updater.start_polling()

test_handler = MessageHandler(Filters.all & (~Filters.command), test)
dispatcher.add_handler(test_handler)
