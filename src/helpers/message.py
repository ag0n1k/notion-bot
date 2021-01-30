from helpers.constants import *
from telegram import ReplyKeyboardMarkup


def get_links(message):
    if message.caption:
        entities = message.caption_entities
        text = message.caption
    else:
        entities = message.entities
        text = message.text
    return parse_links(entities=entities, text=text)


def parse_links(entities, text):
    res = set()
    for entity in entities:
        if entity.type == 'text_link':
            res.add(entity.url)
        elif entity.type == 'url':
            res.add(text[entity.offset:entity.offset + entity.length])
        else:
            print('got unknown type: ', entity.type)
    return res


def command_choose(update):
    update.message.reply_text(
        "Choose an action.",
        reply_markup=ReplyKeyboardMarkup(
            [[KEYBOARD_GET_KEY, KEYBOARD_REMOVE_KEY, KEYBOARD_UPDATE_KEY, KEYBOARD_SYNC_KEY]],
            one_time_keyboard=True)
    )


def category_choose(update, context, message="Choose category."):
    update.message.reply_text(
        message, reply_markup=ReplyKeyboardMarkup([context.categories.names], one_time_keyboard=True)
    )


def domain_choose(update, context, message="Choose domain."):
    update.message.reply_text(
        message, reply_markup=ReplyKeyboardMarkup([context.categories.domains], one_time_keyboard=True)
    )
