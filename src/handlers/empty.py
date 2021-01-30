from base.context import NBotContext
from helpers.decorators import init_context
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)


@init_context
def not_implemented(update, context: NBotContext):
    update.message.reply_text("Not implemented yet.")
    return ConversationHandler.END
