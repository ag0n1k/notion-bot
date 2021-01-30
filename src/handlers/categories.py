from base.utils import get_domain
from base.context import NBotContext
from helpers.decorators import init_context
from helpers.constants import *
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)

DOC_PATH = """
start: category
  >> get: -> get_categories
  >> remove: -> choose_category -> remove_category

start: choose_category -> set_category
"""


@init_context
def get_categories(update, context: NBotContext):
    update.message.reply_text(
        "The categories are:\n{}".format(context.categories),
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


@init_context
def choose_category(update, context: NBotContext):
    update.message.reply_text(
        "Choose the category to remove.",
        reply_markup=ReplyKeyboardMarkup([context.categories.names], one_time_keyboard=True)
    )
    return RM_CATEGORY


@init_context
def remove_category(update, context: NBotContext):
    del context.categories[update.message.text]
    update.message.reply_text(
        "Category removed. Current categories: {}".format("\n".join(context.categories)),
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


@init_context
def set_category(update, context: NBotContext):
    context.categories.update(update.message.text)
    context.categories[update.message.text].update(get_domain(context.current_link))
    update.message.reply_text("Now re-send me the link: {}".format(context.current_link))
    context.clear()
    context.save()
    return ConversationHandler.END
