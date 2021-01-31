import os
import logging
from base.bot import NBot
from base.conversation import NBotConversation
from base.clients import NBotClient, NBotS3Client

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    bot = NBot(os.environ.get('TELEGRAM_TOKEN'))
    notion_client = NBotClient(os.environ.get('NOTION_TOKEN'))
    s3_client = NBotS3Client()
    dialog = NBotConversation()

    bot.register_conversation(dialog.conversation)
    logger.info("NBot starting")
    bot.start()
