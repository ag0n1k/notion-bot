from base.converstations import NBotConversationMain
from clients.notion_db import NBotClient
from clients.omdb import NBotOMDBClient
from telegram.ext import Updater
import logging
import os


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


def main():
    NBotClient(token=os.environ.get('NOTION_TOKEN'))
    NBotOMDBClient(api_key=os.environ.get('OMDB_API_KEY'))
    updater = Updater(os.getenv('TELEGRAM_TOKEN'), use_context=True)
    dispatcher = updater.dispatcher

    main_ = NBotConversationMain()

    dispatcher.add_handler(main_.conversation)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
