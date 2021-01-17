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

START, CHOOSING, ENTRY, TYPING_CHOICE, SET_NOTION_LINK = range(5)


def init_context(user, context):
    notion_token = os.getenv('NOTION_TOKEN')
    context.user_data['bot_context'] = NotionContext(user=user, bot=context.bot, token=notion_token)
    context.user_data['bot_context'].connect2notion()
    if context.user_data['bot_context'].is_connected2notion():
        return ENTRY
    return SET_NOTION_LINK


def context_inited(user, context):
    try:
        _ = context.user_data['bot_context']
    except KeyError:
        if init_context(user, context) == SET_NOTION_LINK:
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
    context.user_data['bot_context'].process(message.urls, update.effective_chat.id)


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
    if not context_inited(update.message.chat['username'], context):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START
    print("load")
    print("for link chose link or content")
    print("sync link in links")
    print("save content in contents")
    update.message.reply_text("urls: " + "\n".join(context.user_data['bot_context'].urls))
    return ConversationHandler.END


def process_url(update, context):
    reply_keyboard = [['Next', 'Stop']]
    try:
        url = context.user_data['bot_context'].urls.pop()
        update.message.reply_text(
            "Process the url: {}".format(url),
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        context.user_data['bot_context'].save_urls()
    except IndexError:
        update.message.reply_text("All urls processed. Congratulations!")
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
            CommandHandler("get", load),
            CommandHandler("start", start),
            CommandHandler("domain", domain),
            CommandHandler("get_domains", get_domains),
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
            CHOOSING: [MessageHandler(Filters.regex('^(Next)$'), process_url),]
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
