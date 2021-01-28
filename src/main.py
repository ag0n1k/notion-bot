import os

from telegram.ext import CommandHandler, CallbackQueryHandler

from bot import NBot
from base.clients import NBotClient, NBotS3Client

from handlers.start import hanlder_start
# from handlers.submit import submit_handler
# from handlers.play_out import play_out_handler


if __name__ == '__main__':
    bot = NBot(os.environ.get('BOT_TOKEN'))
    notion_client = NBotClient(os.environ.get('NOTION_TOKEN'))
    s3_client = NBotS3Client()
    # handlers = [
    #     CommandHandler('start', hanlder_start),
    #
        # CommandHandler('play_out', play_out_handler),
        #
        # CallbackQueryHandler(hanlder_start, pattern='^main$'),
        # CallbackQueryHandler(submit_handler, pattern='^submit$')
    # ]
    # bot.register_handler(handlers)
    #
    # bot.start()