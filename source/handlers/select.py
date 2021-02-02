import logging
from base.constants import *
from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
)

from context import NBotContext
from base.decorators import check_context

logger = logging.getLogger(__name__)


def category(update: Update, context: CallbackContext) -> None:
    # update.callback_query.answer()
    update.callback_query.edit_message_text(text="category")
    # update.message.reply_text(text="category")
    return ConversationHandler.END


@check_context
def notion(update: Update, context: NBotContext) -> None:
    # update.callback_query.answer()
    buttons = [[
            InlineKeyboardButton(text='Create', callback_data=str(CREATE)),
            InlineKeyboardButton(text='Remove', callback_data=str(REMOVE)),
            InlineKeyboardButton(text='Exit', callback_data=str(ConversationHandler.END)),
    ]]

    update.callback_query.edit_message_text(
        text="Create or remove...",
        reply_markup=InlineKeyboardMarkup(buttons))
    return SELECTING_ACTION


@check_context
def create(update: Update, context: NBotContext) -> None:
    buttons = [[
        InlineKeyboardButton(text=NOTION_CINEMA_TYPE, callback_data=str(CINEMA)),
        InlineKeyboardButton(text=NOTION_LINK_TYPE, callback_data=str(LINK)),
        InlineKeyboardButton(text='Exit', callback_data=str(ConversationHandler.END)),
    ]]
    update.callback_query.edit_message_text(
        text="Choose a type",
        reply_markup=InlineKeyboardMarkup(buttons))
    return ConversationHandler.END
    # update.message.reply_text(text="notion")
