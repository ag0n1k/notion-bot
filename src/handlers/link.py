from helpers.decorators import init_context
from base.context import NBotContext
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)


@init_context
def get(update, context: NBotContext):
    if context.links:
        update.message.reply_text(
            "The links are: {}".format("\n".join(context.links)),
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        update.message.reply_text("No saved links are here", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


@init_context
def set_(update, context: NBotContext):
    logger.info(context.username)
    if not context.connected:
        context.dblink = update.message.text
        context.connect()
        context.save()
    update.message.reply_text("Bot successfully connected to the notion. Send me the links.")
    return ConversationHandler.END
