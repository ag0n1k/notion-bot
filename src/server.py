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
from yc_s3 import NotionBotS3Client
from t_help import TelegramMessageUrl

START, CHOOSING, ENTRY, TYPING_CHOICE, SET_NOTION_LINK = range(5)

NOTION_DB_TEMPLATE = "{user}_notion_db.json"
NOTION_URL_TEMPLATE = "{user}_url_{ts}.json"

s3_client = NotionBotS3Client()


def init_context(username, context):
    notion_token = os.getenv('NOTION_TOKEN')
    context.user_data['bot_context'] = NotionContext(
        s3_client=s3_client, username=username, bot=context.bot, token=notion_token)
    context.user_data['bot_context'].connect2notion()
    if context.user_data['bot_context'].is_connected2notion():
        return ENTRY
    return SET_NOTION_LINK


def context_inited(username, context):
    try:
        _ = context.user_data['bot_context']
    except KeyError:
        if init_context(username, context) == SET_NOTION_LINK:
            return False
    except Exception as e:
        raise e
    return True


def links(update, context):
    if not context_inited(update.message.chat['username'], context):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START

    message = TelegramMessageUrl(update.message)
    message.parse_urls()
    for url in message.urls:
        context.user_data['bot_context'].process(url, update.effective_chat.id)


def start(update, context):
    update.message.reply_text(
        "Hi, this is notion link care bot that take care of your links in notion.\n"
        "Okay, now we have 3 actions to be done:\n"
        "  1) Choose a link database\n"
        "  2) Add me (notion-link.care@yandex.ru) with edit permissions\n"
        "  3) Share the link to me. Like:\n"
        "https://www.notion.so/<namespace>/<db_hash>?v=<view_hash>"
    )
    return init_context(update.message.chat['username'], context)


def set_notion_link(update, context):
    if not context_inited(update.message.chat['username'], context):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START
    context.user_data['bot_context'].set_notion_link(update.message.text)
    context.user_data['bot_context'].save_link()
    context.user_data['bot_context'].connect2notion()
    update.message.reply_text("Excellent, now you can send me the links")
    return ENTRY


def optout(update, context):
    update.message.reply_text("Not implemented yet")
    return


# TODO: read about command args
def domain(update, context):
    if not context_inited(update.message.chat['username'], context):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START
    context.user_data['bot_context'].update_domains(context.args)


def get_domains(update, context):
    if not context_inited(update.message.chat['username'], context):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START
    context.user_data['bot_context'].print_domains(update.effective_chat.id)


def done(update, context) -> int:
    update.message.reply_text("Something went wrong...")
    return ConversationHandler.END


def load(update, context) -> int:
    print("load")
    print("for link chose link or content")
    print("sync link in links")
    print("save content in contents")
    return ConversationHandler.END


def main() -> None:
    tgram_token = os.getenv('TELEGRAM_TOKEN')
    if not tgram_token:
        raise ValueError("Telegram token is undefined")
    updater = Updater(token=tgram_token, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.all & (~Filters.command), links),
            CommandHandler("get", load),
            CommandHandler("start", start),
            CommandHandler("domain", domain),
            CommandHandler("get_domains", get_domains),
            CommandHandler("configure", start),
            CommandHandler("optout", optout),
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
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )
    dispatcher.add_handler(CommandHandler("optout", optout))
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
