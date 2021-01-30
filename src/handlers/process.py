from helpers.decorators import init_context
from base.context import NBotContext
from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler
from helpers.constants import *
import logging

logger = logging.getLogger(__name__)


@init_context
def next_or_stop(update, context: NBotContext):
    context.clear()
    update.message.reply_text(
        "Continue?",
        reply_markup=ReplyKeyboardMarkup([[KEYBOARD_NEXT_KEY, KEYBOARD_STOP_KEY]], one_time_keyboard=True),
    )
    return CHOOSING

