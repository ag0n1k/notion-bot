from aiogram import Bot, Dispatcher, executor, types
from clients.notion_db import NBotClient
from clients.omdb import NBotOMDBClient
from schemes.link import NBotLink, NBotCinemaLink, NBotWatchLink
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

import logging
import os
import utils


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)

# Initialize bot and dispatcher
storage = MemoryStorage()
bot = Bot(token=os.environ.get('TELEGRAM_TOKEN'))
dp = Dispatcher(bot, storage=storage)
client = NBotClient(token=os.environ.get('NOTION_TOKEN'))
omdb = NBotOMDBClient(api_key=os.environ.get('OMDB_API_KEY'))

domain_classes = {
    "youtube.com": NBotWatchLink,
    "youtu.be": NBotWatchLink,
    "m.imdb.com": NBotCinemaLink,
    "imdb.com": NBotCinemaLink,
}


class PhotoState(StatesGroup):
    name = State()


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
    await message.reply("Fixed")
    await message.reply("Processed:\n{}".format("\n".join(res)))


@dp.callback_query_handler()
async def inline_kb_answer_callback_handler(query: types.CallbackQuery):
    await query.answer(f'You answered with {query.data!r}')
    for link in utils.parse_links(query.message.reply_to_message.entities, query.message.reply_to_message.text):
        nlink = domain_classes.get(utils.domain(link), NBotLink)(link)
        nlink.process()
        await query.message.edit_text("Processed:\n{}".format(
            client.create_page(client.get_id_by_db_name(query.data), nlink.properties)))
    client.init_maps()


@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    await PhotoState.name.set()
    await message.reply("Name it!")


@dp.message_handler(state=PhotoState.name)
async def process_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['text'] = message.text
        user_message = data['text']

        otvet_klienty = ""
        await bot.send_message(
            message.from_user.id,
            otvet_klienty,
        )

    await state.finish()


def main():
    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':
    main()
