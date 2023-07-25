from aiogram import Bot, Dispatcher, executor, types
from clients.notion_db import NBotClient
from clients.omdb import NBotOMDBClient
from schemes.link import NBotLink, NBotCinemaLink, NBotWatchLink
import utils
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))
dp = Dispatcher(bot)
client = NBotClient(token=os.environ.get('NOTION_TOKEN'))
omdb = NBotOMDBClient(api_key=os.environ.get('OMDB_API_KEY'))

domain_classes = {
    "youtube.com": NBotWatchLink,
    "youtu.be": NBotWatchLink,
    "m.imdb.com": NBotCinemaLink,
    "imdb.com": NBotCinemaLink,
}


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    await message.reply("Hi!\nI'm NotionLinkBot!\nPowered by aiogram.")


@dp.message_handler(commands=['get'])
async def get_handler(message: types.Message):
    """
    This handler will be called when user sends `/start` or `/help` command
    """
    keyboard_markup = types.InlineKeyboardMarkup()
    for db in client.databases:
        keyboard_markup.row(types.InlineKeyboardButton(db, callback_data="get|" + db))
    await message.reply("What is the category you looking for?", reply_markup=keyboard_markup)


@dp.message_handler()
async def main_handler(message: types.Message):
    answer = await message.reply("Got your message ...")
    res = []
    for link in utils.parse_links(message.entities, message.text):
        nlink = domain_classes.get(utils.domain(link), NBotLink)(link)
        db_id = client.get_id_by_domain(nlink.domain)
        if not db_id:
            keyboard_markup = types.InlineKeyboardMarkup()
            for db in client.databases:
                keyboard_markup.row(types.InlineKeyboardButton(db, callback_data="parse|" + db))
            await message.reply("What is the category of this domain? {}".format(nlink.domain),
                                reply_markup=keyboard_markup)
            return
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


@dp.callback_query_handler()
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    action_, data = query.data.split("|")
    await query.answer(f'You answered with {data!r}')
    # todo: split? or case?
    if action_ == 'parse':
        for link in utils.parse_links(query.message.reply_to_message.entities, query.message.reply_to_message.text):
            nlink = domain_classes.get(utils.domain(link), NBotLink)(link)
            nlink.process()
            await query.message.edit_text("Processed:\n{}".format(
                client.create_page(client.get_id_by_db_name(data), nlink.properties, icon=nlink.icon)))
        client.init_maps()
    elif action_ == 'get':
        page_ = client.get_random_page_from_db(client.get_id_by_db_name(data))
        await query.message.edit_text(f"{data}:\n - {page_['properties']['URL']['url']}\n - {page_['url']}")


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
