import logging
import os

from handlers.entry_points import start, process
from constants import *
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
)

# Enable logging
from handlers.select import category, notion

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)

logger = logging.getLogger(__name__)


def stop(update: Update, context: CallbackContext) -> None:
    """End Conversation by command."""
    update.message.reply_text('Okay, bye.')

    return ConversationHandler.END


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(os.getenv('TELEGRAM_TOKEN'), use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # Set up third level ConversationHandler (collecting features)

    # Set up top level ConversationHandler (selecting action)
    # Because the states of the third level conversation map to the ones of the econd level
    # conversation, we need to make sure the top level conversation can also handle them
    selection_handlers = [
        CallbackQueryHandler(category, pattern='^' + str(CATEGORY) + '$'),
        CallbackQueryHandler(notion, pattern='^' + str(NOTION) + '$'),
    ]
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CommandHandler('configure', start),
            MessageHandler(Filters.all, process),
        ],
        states={
            SELECTING_ACTION: selection_handlers,
            SELECTING_LEVEL: selection_handlers,
            STOPPING: [CommandHandler('start', start)],
        },
        fallbacks=[CommandHandler('stop', stop)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
