import json

from aiogram import Bot, Dispatcher, types, Router
from clients.notion_db import NBotClient
from clients.omdb import NBotOMDBClient
from schemes.link import NBotLink, NBotCinemaLink, NBotWatchLink

from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

import logging
import os
import utils
import sys

# Configure logging
root = logging.getLogger()
root.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
root.addHandler(handler)

logger = logging.getLogger(__name__)


bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))
router = Router(name=__name__)
dp = Dispatcher()
client = NBotClient(token=os.environ.get('NOTION_TOKEN'))
omdb = NBotOMDBClient(api_key=os.environ.get('OMDB_API_KEY'))

domain_classes = {
    "youtube.com": NBotWatchLink,
    "youtu.be": NBotWatchLink,
    "m.imdb.com": NBotCinemaLink,
    "imdb.com": NBotCinemaLink,
}


@router.message(CommandStart())
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm NotionLinkBot!\nPowered by aiogram.")


@router.message(Command("get"))
async def get_handler(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    builder = InlineKeyboardBuilder()
    for db in client.databases:
        builder.add(InlineKeyboardButton(text=db, callback_data="get|" + db))
    builder.adjust(3, 2)
    await message.reply("What is the category you looking for?", reply_markup=builder.as_markup())


async def register_handlers(dp: Dispatcher):
    """Registration all handlers before processing update."""
    dp.message.register(main_handler)
    dp.message.register(send_welcome)
    dp.message.register(get_handler)
    dp.callback_query.register(inline_kb_answer_callback_handler)
    logger.info('Handlers are registered.')


async def handler(event, context):
    """Yandex.Cloud functions handler."""
    logger.info('Registering handlers.')

    await register_handlers(dp)
    logger.info('Wait for data...')
    await dp.feed_webhook_update(bot, types.update.Update(**json.loads(event['body'])))

    return {'statusCode': 200, 'body': 'ok'}


@router.message()
async def main_handler(message: types.Message):

    res = []
    for link in utils.parse_links(message.entities, message.text):
        nlink = domain_classes.get(utils.domain(link), NBotLink)(link)
        db_id = client.get_id_by_domain(nlink.domain)
        if not db_id:
            builder = InlineKeyboardBuilder()
            for db in client.databases:
                builder.add(InlineKeyboardButton(text=db, callback_data="parse|" + db))
            builder.adjust(3, 2)
            await message.reply("What is the category of this domain? {}".format(nlink.domain),
                                reply_markup=builder.as_markup())
            return
        answer = await message.reply("Got your message ...")
        page_ = client.search_by_url(database_id=db_id, name=nlink.link)

        if not page_:
            await answer.edit_text("Creating new page ...")
            nlink.process()
            page_ = client.create_page(client.get_id_by_domain(nlink.domain), nlink.properties, icon=nlink.icon)
        res.append(page_['url'])
        blocks = client.client.blocks.children.list(page_['id'])
        if len(blocks['results']) == 0:
            await answer.edit_text("Updating content...")
            children = nlink.blocks(blocks)
            for chunk in utils.chunks(children, 100):
                client.client.blocks.children.append(block_id=page_['id'], children=chunk)
    await answer.edit_text("Processed:\n{}".format("\n".join(res)))


@router.callback_query()
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    action_, data = query.data.split("|")
    await query.answer(f'You answered with {data!r}')
    # todo: split? or case?
    if action_ == 'parse':
        for link in utils.parse_links(query.message.reply_to_message.entities, query.message.reply_to_message.text):
            nlink = domain_classes.get(utils.domain(link), NBotLink)(link)
            nlink.process()
            page_ = client.create_page(client.get_id_by_db_name(data), nlink.properties, icon=nlink.icon)
            await query.message.edit_text("Processed:\n{}".format(page_['url']))
        client.init_maps()
    elif action_ == 'get':
        page_ = client.get_random_page_from_db(client.get_id_by_db_name(data))
        await query.message.edit_text(f"{data}:\n - {page_['properties']['URL']['url']}\n - {page_['url']}")
