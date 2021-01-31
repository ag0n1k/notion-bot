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
    update.message.reply_text("\n".join(context.categories.domains), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


@init_context
def choose(update, context: NBotContext):
    domain_choose(update, context, message="Choose the category to remove.")
    return RM_DOMAIN


@init_context
def remove(update, context: NBotContext):
    context.categories.remove_domain(update.message.text)
    update.message.reply_text("Domain removed", reply_markup=ReplyKeyboardRemove())
    context.save()
    return ConversationHandler.END


@init_context
def sync(update, context: NBotContext):
    update.message.reply_text(context.sync_domains())
    return ConversationHandler.END
