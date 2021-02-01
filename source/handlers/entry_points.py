from telegram import InlineKeyboardMarkup, InlineKeyboardButton, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
)

from constants import *
from context import NBotContext
from decorators import check_context


@check_context
def start(update: Update, context: NBotContext) -> None:
    text = (
        'Welcome to the menu'
    )
    buttons = [[
            InlineKeyboardButton(text='Notion', callback_data=str(NOTION)),
            InlineKeyboardButton(text='Category', callback_data=str(CATEGORY)),
            InlineKeyboardButton(text='Done', callback_data=str(ConversationHandler.END)),
    ]]
    # If we're starting over we don't need do send a new message
    if context.start_over:
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))

    context.start_over = False
    return SELECTING_ACTION


@check_context
def process(update: Update, context: NBotContext) -> None:
    update.message.reply_text(text=update.message.text + " " + str(context.__dict__))
    return ConversationHandler.END
