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


@dp.message_handler()
async def echo(message: types.Message):
    res = []
    for link in utils.parse_links(message.entities, message.text):
        nlink = domain_classes.get(utils.domain(link), NBotLink)(link)
        if not client.get_id_by_domain(nlink.domain):
            keyboard_markup = types.InlineKeyboardMarkup()
            for db in client.databases:
                keyboard_markup.row(types.InlineKeyboardButton(db, callback_data=db))
            await message.reply("What is the category of this domain? {}".format(nlink.domain),
                                reply_markup=keyboard_markup)
            return
        nlink.process()
        res.append(client.create_page(client.get_id_by_domain(nlink.domain), nlink.properties))
    await message.reply("Processed:\n{}".format("\n".join(res)))


@dp.callback_query_handler()
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    await query.answer(f'You answered with {query.data!r}')
    link = query.message.reply_to_message.text
    nlink = domain_classes.get(utils.domain(link), NBotLink)(link)
    nlink.process()
    await query.message.edit_text("Processed:\n{}".format(
        client.create_page(client.get_id_by_db_name(query.data), nlink.properties)))
    client.init_maps()


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
