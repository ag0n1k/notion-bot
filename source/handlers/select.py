import logging
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

logger = logging.getLogger(__name__)


def category(update: Update, context: CallbackContext) -> None:
    # update.callback_query.answer()
    update.callback_query.edit_message_text(text="category")
    # update.message.reply_text(text="category")
    return ConversationHandler.END


def notion(update: Update, context: CallbackContext) -> None:
    # update.callback_query.answer()
    update.callback_query.edit_message_text(text="notion")
    # update.message.reply_text(text="notion")
    return ConversationHandler.END
