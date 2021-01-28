from helpers.decorators import init_context
from context import NBotContext
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler

from helpers.constants import *

DOC_PATH = """
start: category
  >> get: -> get_categories
  >> remove: -> choose_category -> remove_category
"""


@init_context
def handler_category(update, context: NBotContext):
    if not context.connected:
        return SET_LINK
    update.message.reply_text(
        "Choose an action.",
        reply_markup=ReplyKeyboardMarkup([[KEYBOARD_GET_KEY, KEYBOARD_REMOVE_KEY]], one_time_keyboard=True)
    )
    return CATEGORY


@init_context
def get_categories(update, context: NBotContext):
    update.message.reply_text(
        "The categories are: "
        "\n".join(context.category_values),
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


@init_context
def choose_category(update, context: NBotContext):
    update.message.reply_text(
        "Choose the category to remove.",
        reply_markup=ReplyKeyboardMarkup([context.category_names], one_time_keyboard=True)
    )
    return RM_CATEGORY


@init_context
def remove_category(update, context: NBotContext):
    context.del_category(update.message.text)
    update.message.reply_text(
        "Category removed. Current categories: {}".format("\n".join(context.category_values)),
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END
