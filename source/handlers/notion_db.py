from base.constants import *
from telegram import ReplyKeyboardMarkup, Update

from context import NBotContext
from base.decorators import check_context

class NBotConverstaion():


@check_context
def create(update: Update, context: NBotContext) -> None:
    update.message.reply_text(
        "Choose a type", reply_markup=ReplyKeyboardMarkup([NOTION_TYPES], one_time_keyboard=True)
    )
    return GATHER


@check_context
def set_(update: Update, context: NBotContext) -> None:
    update.message.reply_text(
        "Choose a type", reply_markup=ReplyKeyboardMarkup([NOTION_TYPES], one_time_keyboard=True)
    )
    return SET_


@check_context
def set_(update: Update, context: NBotContext) -> None:
    update.message.reply_text(
        "Choose a type", reply_markup=ReplyKeyboardMarkup([NOTION_TYPES], one_time_keyboard=True)
    )
    return SET_LINK


@check_context
def set_(update: Update, context: NBotContext) -> None:
    update.message.reply_text(
        "Choose a type", reply_markup=ReplyKeyboardMarkup([NOTION_TYPES], one_time_keyboard=True)
    )
    return CONNECT


@check_context
def remove(update: Update, context: NBotContext) -> None:
    update.message.reply_text(
        "Choose a type", reply_markup=ReplyKeyboardMarkup([NOTION_TYPES], one_time_keyboard=True)
    )
    return CONNECT
