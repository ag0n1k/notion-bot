import os
import logging
from bot import NBot
from base.clients import NBotClient, NBotS3Client
from handlers.conversation import Conversation

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    bot = NBot(os.environ.get('TELEGRAM_TOKEN'))
    notion_client = NBotClient(os.environ.get('NOTION_TOKEN'))
    s3_client = NBotS3Client()
    dialog = Conversation()

    bot.register_conversation(dialog.conversation)
    logger.info("NBot starting")
    bot.start()
