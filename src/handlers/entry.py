from helpers.decorators import init_context
from context import NBotContext
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from helpers.message import get_links
from helpers.constants import *
import logging

logger = logging.getLogger(__name__)


@init_context
def handler_entry(update, context: NBotContext):
    logger.info(context.username)
    update.message.reply_text(
        "Processed links: {}".format("\n".join(context.process(get_links(update.message)))),
    )
    logger.info("Processed the message for the user: {}".format(context.username))
    return ConversationHandler.END

