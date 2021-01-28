from helpers.decorators import init_context
from context import NBotContext
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
from helpers.message import get_links
from helpers.constants import *
import logging

logger = logging.getLogger(__name__)


@init_context
def handler_process(update, context: NBotContext):
    context.current_link = context.links.pop()
    update.message.reply_text(
        "Process the url: {}".format(context.current_link),
        reply_markup=ReplyKeyboardMarkup([[KEYBOARD_MANUAL_KEY, KEYBOARD_AUTO_KEY]], one_time_keyboard=True),
    )


@init_context
def next_or_stop(update, context: NBotContext):
    context.current_link = ""
    update.message.reply_text(
        "Continue?",
        reply_markup=ReplyKeyboardMarkup([[KEYBOARD_NEXT_KEY, KEYBOARD_STOP_KEY]], one_time_keyboard=True),
    )
