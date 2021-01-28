import logging
from context import NBotContext
from helpers.constants import *
from helpers.decorators import init_context
from telegram.ext import ConversationHandler

logger = logging.getLogger(__name__)


@init_context
def handler_start(update, context: NBotContext):
    if context.connected:
        update.message.reply_text("Bot successfully connected to the notion. Send me the links.")
        return ConversationHandler.END
    logger.info("Context not connected {}".format(SET_LINK))
    update.message.reply_text(
        "Hi, this is notion link care bot that take care of your links in notion.\n"
        "Okay, now we have 3 actions to be done:\n"
        "  1) Choose a link database (e.g. My Links)\n"
        "  2) Add me (notion-link.care@yandex.ru) with edit permissions\n"
        "  3) Share the link to me. Like:\n"
        "https://www.notion.so/<namespace>/<db_hash>?v=<view_hash>"
    )
    return SET_LINK


@init_context
def set_link(update, context: NBotContext):
    if not context.connected:
        context.dblink = update.message.text
        context.connect()
        context.save()
    update.message.reply_text("Bot successfully connected to the notion. Send me the links.")
    return ENTRY
