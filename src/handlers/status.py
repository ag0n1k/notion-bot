from base.context import NBotContext
from helpers.message import domain_choose
from helpers.decorators import init_context
from helpers.constants import *
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)


@init_context
def get(update, context: NBotContext):
    update.message.reply_text("\n".join(context.statuses), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


@init_context
def rand(update, context: NBotContext):
    update.message.reply_text(context.sync_domains())
    return ConversationHandler.END
