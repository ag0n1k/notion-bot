from base.context import NBotContext
from helpers.constants import *
from helpers.decorators import init_context
from helpers.message import get_links, command_choose
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

    update.message.reply_text(
        "Process the link:\n{}".format(context.current_link),
        reply_markup=ReplyKeyboardMarkup([[KEYBOARD_MANUAL_KEY, KEYBOARD_AUTO_KEY]], one_time_keyboard=True),
    )
    return CHOOSING
