from base.context import NBotContext
from helpers.message import category_choose
from helpers.decorators import init_context
from base.constants import *
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)


@init_context
def get(update, context: NBotContext):
    category_choose(update, context)
    return GET_STATUS


@init_context
def rand(update, context: NBotContext):
    update.message.reply_text(context.get_rand(update.message.text))
    return ConversationHandler.END
