from base.context import NBotContext
from helpers.constants import *
from helpers.decorators import init_context
from helpers.message import get_links, choose
from telegram.ext import ConversationHandler

import logging

logger = logging.getLogger(__name__)


@init_context
def handler_entry(update, context: NBotContext):
    update.message.reply_text(
        "Processed links: {}".format("\n".join(context.process(get_links(update.message)))),
    )
    logger.info("Processed the message for the user: {}".format(context.username))
    return ConversationHandler.END


@init_context
def handler_category(update, context: NBotContext):
    choose(update=update)
    return CATEGORY
