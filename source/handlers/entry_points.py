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


# Top level conversation callbacks
from context import NBotContext
from decorators import check_context


def start(update: Update, context: CallbackContext) -> None:
    text = (
        'Welcome to the menu'
    )
    buttons = [
        [
            InlineKeyboardButton(text='Notion', callback_data=str(NOTION)),
        ],
        [
            InlineKeyboardButton(text='Category', callback_data=str(CATEGORY)),
        ],
        [
            InlineKeyboardButton(text='Done', callback_data=str(ConversationHandler.END)),
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # If we're starting over we don't need do send a new message
    if context.user_data.get(START_OVER):
        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    else:
        update.message.reply_text(text=text, reply_markup=keyboard)

    context.user_data[START_OVER] = False
    return SELECTING_ACTION


@check_context
def process(update: Update, context: NBotContext) -> None:
    update.message.reply_text(text=update.message.text + str(context.__dict__))
    return ConversationHandler.END
