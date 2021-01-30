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
def get_domains(update, context: NBotContext):
    update.message.reply_text("\n".join(context.categories.domains), reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


@init_context
def choose_domain(update, context: NBotContext):
    update.message.reply_text(
        "Choose the category to remove.",
        reply_markup=ReplyKeyboardMarkup([context.categories.domains], one_time_keyboard=True)
    )
    return RM_CATEGORY


@init_context
def remove_domain(update, context: NBotContext):
    context.categories.remove_domain(update.message.text)
    update.message.reply_text(
        "Category removed. Current categories: {}".format("\n".join(context.categories)),
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


@init_context
def set_domain(update, context: NBotContext):
    context.categories.update(update.message.text)
    context.categories[update.message.text].update(get_domain(context.current_link))
    update.message.reply_text("Now re-send me the link: {}".format(context.current_link))
    context.clear()
    context.save()
    return ConversationHandler.END
