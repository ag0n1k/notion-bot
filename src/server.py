from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import os
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)

from notion_bot import NotionContext
from telegram_helper import TelegramMessageUrl

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

START, CHOOSING, ENTRY, TYPING_CHOICE, SET_NOTION_LINK, CATEGORY = range(6)


def init_context(user, context, chat_id):
    notion_token = os.getenv('NOTION_TOKEN')
    context.user_data['bot_context'] = NotionContext(user=user, bot=context.bot, token=notion_token, chat_id=chat_id)
    try:
        context.user_data['bot_context'].connect()
        if context.user_data['bot_context'].connected:
            return ENTRY
    except AttributeError:
        # no link found
        pass
    return SET_NOTION_LINK


def context_inited(user, context, chat_id):
    try:
        _ = context.user_data['bot_context']
    except KeyError:
        if init_context(user, context, chat_id) == SET_NOTION_LINK:
            return False
    except Exception as e:
        raise e
    return True


def links(update, context):
    if not context_inited(update.message.chat['username'], context, update.effective_chat.id):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START

    message = TelegramMessageUrl(update.message)
    message.parse_urls()
    context.user_data['bot_context'].process(message.urls)


def start(update, context):
    update.message.reply_text(
        "Hi, this is notion link care bot that take care of your links in notion.\n"
        "Okay, now we have 3 actions to be done:\n"
        "  1) Choose a link database\n"
        "  2) Add me (notion-link.care@yandex.ru) with edit permissions\n"
        "  3) Share the link to me. Like:\n"
        "https://www.notion.so/<namespace>/<db_hash>?v=<view_hash>"
    )
    return init_context(update.message.chat['username'], context, update.effective_chat.id)


def set_notion_link(update, context):
    if not context_inited(update.message.chat['username'], context, update.effective_chat.id):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START
    context.user_data['bot_context'].link = update.message.text
    context.user_data['bot_context'].save_link()
    context.user_data['bot_context'].connect()
    update.message.reply_text("Excellent, now you can send me the links")
    return ENTRY


def optout(update, context):
    update.message.reply_text("Not implemented yet")
    return ConversationHandler.END


def get_categories(update, context):
    if not context_inited(update.message.chat['username'], context, update.effective_chat.id):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START
    context.user_data['bot_context'].print_domains()
    return ConversationHandler.END


def update_categories(update, context):
    if not context_inited(update.message.chat['username'], context, update.effective_chat.id):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START
    if not context.user_data['process_url']:
        update.message.reply_text("Missed the link",
                                  reply_markup=ReplyKeyboardMarkup([['Next', 'Stop']], one_time_keyboard=True),)
        return ConversationHandler.END
    update.message.reply_text(
        "Choose category or send a new one",
        reply_markup=ReplyKeyboardMarkup([context.user_data['bot_context'].get_categories()], one_time_keyboard=True)
    )
    return CATEGORY


def set_category(update, context):
    if not context_inited(update.message.chat['username'], context, update.effective_chat.id):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START

    context.user_data['bot_context'].update_domain(update.message.text, context.user_data['process_url'])
    update.message.reply_text("Now resend me this message with url: {}".format(context.user_data['process_url']))
    return ConversationHandler.END


def remove_category(update, context):
    if not context_inited(update.message.chat['username'], context, update.effective_chat.id):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START

    update.message.reply_text(
        "Choose the category to remove.",
        reply_markup=ReplyKeyboardMarkup([context.user_data['bot_context'].get_categories()], one_time_keyboard=True)
    )
    return RM_CATEGORY


def rm_category(update, context):
    context.user_data['bot_context'].remove_category(update.message.text)
    return ConversationHandler.END


def done(update, context) -> int:
    update.message.reply_text("Something went wrong...")
    return ConversationHandler.END


def get_urls(update, context) -> int:
    if not context_inited(update.message.chat['username'], context, update.effective_chat.id):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START
    update.message.reply_text("\n".join(context.user_data['bot_context'].urls))
    return ConversationHandler.END


def next_or_stop(update, context):
    update.message.reply_text(
        "Processed the url: {}.\nGoing next?".format(context.user_data['process_url']),
        reply_markup=ReplyKeyboardMarkup([['Next', 'Stop']], one_time_keyboard=True),
    )
    context.user_data['bot_context'].save_urls()
    return CHOOSING


def process_url(update, context):
    if not context_inited(update.message.chat['username'], context, update.effective_chat.id):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START
    try:
        context.user_data['process_url'] = context.user_data['bot_context'].urls.pop()
        update.message.reply_text(
            "Process the url: {}".format(context.user_data['process_url']),
            reply_markup=ReplyKeyboardMarkup([['Manual', 'Auto']], one_time_keyboard=True),
        )
    except IndexError:
        update.message.reply_text("All urls processed. Congratulations!")
        return ENTRY
    return CHOOSING


def main() -> None:
    tgram_token = os.getenv('TELEGRAM_TOKEN')
    if not tgram_token:
        raise ValueError("Telegram token is undefined")
    updater = Updater(token=tgram_token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.all & (~Filters.command), links),
            CommandHandler("start", start),
            CommandHandler("categories", get_categories),
            CommandHandler("links", get_urls),
            CommandHandler("remove_category", remove_category),
            CommandHandler("configure", start),
            CommandHandler("optout", optout),
            CommandHandler("process", process_url),
            # todo: add command for the contents works (save_content)
            # MessageHandler(Filters.command, content_load),
        ],
        states={
            START: [
                CommandHandler("start", start),
                MessageHandler(Filters.all & (~Filters.command), start),
            ],
            ENTRY: [MessageHandler(Filters.all & (~Filters.command), links)],
            SET_NOTION_LINK: [MessageHandler(Filters.all, set_notion_link)],
            CHOOSING: [
                MessageHandler(Filters.regex('^(Next)$'), process_url),
                MessageHandler(Filters.regex('^(Manual)$'), next_or_stop),
                MessageHandler(Filters.regex('^(Auto)$'), update_categories),
            ],
            CATEGORY: [MessageHandler(Filters.all, set_category)],
            RM_CATEGORY: [MessageHandler(Filters.all, rm_category)],
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
