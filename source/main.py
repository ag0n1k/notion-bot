import logging
import os

from handlers.entry_points import start, process
from base.constants import *
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from base.converstations import NBotConversationMain
# Enable logging
from handlers.select import category, notion, create

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


def stop(update: Update, context: CallbackContext) -> None:
    """End Conversation by command."""
    text = 'Okay, bye.'
    if update.message:
        update.message.reply_text(text=text)
    else:
        update.callback_query.edit_message_text(text=text)
    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.getenv('TELEGRAM_TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # selection_handlers = [
    #     CallbackQueryHandler(category, pattern='^' + str(CATEGORY) + '$'),
    #     CallbackQueryHandler(notion, pattern='^' + str(NOTION) + '$'),
    #     CallbackQueryHandler(create, pattern='^' + str(CREATE) + '$'),
    #     CallbackQueryHandler(create, pattern='^' + str(REMOVE) + '$'),
    #     CallbackQueryHandler(stop, pattern='^' + str(ConversationHandler.END) + '$'),
    # ]
    # notion_handler = ConversationHandler(
    #     entry_points=[],
    #     states={},
    #     fallbacks=[]
    # )
    # category_handler = ConversationHandler(
    #     entry_points=[],
    #     states={},
    #     fallbacks=[]
    # )
    # conv_handler = ConversationHandler(
    #     entry_points=[
    #         CommandHandler('start', start),
    #         CommandHandler('configure', start),
    #         MessageHandler(Filters.all, process),
    #     ],
    #     states={
    #         CATEGORY: selection_handlers,
    #         NOTION: selection_handlers,
    #         CONNECT: [],
    #         STOPPING: [CommandHandler('start', start)],
    #     },
    #     fallbacks=[CommandHandler('stop', stop)],
    # )
    #
    main_ = NBotConversationMain()
    dispatcher.add_handler(main_.conversation)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
