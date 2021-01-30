from base.utils import get_domain
from base.context import NBotContext
from helpers.decorators import init_context
from helpers.constants import *
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ConversationHandler
import logging

logger = logging.getLogger(__name__)


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
    return RM_DOMAIN


@init_context
def remove_domain(update, context: NBotContext):
    if context.categories.remove_domain(update.message.text):
        update.message.reply_text("Domain removed", reply_markup=ReplyKeyboardRemove())
    else:
        update.message.reply_text("No domain were removed", reply_markup=ReplyKeyboardRemove(),)
    return ConversationHandler.END
