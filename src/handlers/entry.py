from base.context import NBotContext
from helpers.constants import *
from helpers.decorators import init_context
from helpers.message import get_links, command_choose, process_link
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)


@init_context
def main(update, context: NBotContext):
    update.message.reply_text(
        "Processed links:\n{}".format("\n".join(context.process(get_links(update.message)))),
    )
    return ConversationHandler.END


@init_context
def category(update, context: NBotContext):
    command_choose(update=update)
    return CATEGORY


@init_context
def domain(update, context: NBotContext):
    command_choose(update=update)
    return DOMAIN


@init_context
def link(update, context: NBotContext):
    command_choose(update=update)
    return LINK


@init_context
def process(update, context: NBotContext):
    if not context.last_link:
        update.message.reply_text("No links to process!")
        return ConversationHandler.END

    process_link(update, context, link=context.current_link)
    return CHOOSING


@init_context
def start(update, context: NBotContext):
    logger.info(context.username)
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
