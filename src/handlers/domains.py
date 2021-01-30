from base.utils import get_domain
from base.context import NBotContext
from helpers.message import domain_choose
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
    domain_choose(update, context, message="Choose the category to remove.")
    return RM_DOMAIN


@init_context
def remove_domain(update, context: NBotContext):
    context.categories.remove_domain(update.message.text)
    update.message.reply_text("Domain removed", reply_markup=ReplyKeyboardRemove())
    context.save()
    return ConversationHandler.END
