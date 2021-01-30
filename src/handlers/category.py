from base.utils import get_domain
from base.context import NBotContext
from helpers.constants import *
from helpers.decorators import init_context
from helpers.message import category_choose
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)


@init_context
def get(update, context: NBotContext):
    update.message.reply_text("\n".join(context.categories.view), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


@init_context
def choose(update, context: NBotContext):
    category_choose(update, context, message="Choose the category to remove.")
    return RM_CATEGORY


@init_context
def choose_create(update, context: NBotContext):
    category_choose(update, context, message="Choose the category or send a new one.")
    return SET_CATEGORY


@init_context
def remove(update, context: NBotContext):
    del context.categories[update.message.text]
    update.message.reply_text("Category removed.", reply_markup=ReplyKeyboardRemove())
    context.save()
    return ConversationHandler.END


@init_context
def set(update, context: NBotContext):
    context.categories.update(update.message.text)
    context.categories[update.message.text].update(get_domain(context.current_link))
    update.message.reply_text("Now re-send me the link: {}".format(context.current_link))
    context.clear()
    context.save()
    return ConversationHandler.END


@init_context
def sync(update, context: NBotContext):
    context.sync_categories()
    return ConversationHandler.END
