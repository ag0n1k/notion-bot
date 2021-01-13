from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
from notion_link import NotionBotClient
from notion_db import NotionUrl
from settings import (
    TGRAM_TOKEN,
)
from yc_s3 import NotionBotS3Client
from t_help import TelegramMessageUrl

START, CHOOSING, ENTRY, TYPING_CHOICE, SET_NOTION_LINK, SET_NOTION_TOKEN = range(6)

link_domain = (
        'youtube.com',
        'twitch.com',
    )

NOTION_TOKEN_TEMPLATE = "{user}_notion_token.json"
NOTION_URL_TEMPLATE = "{user}_url_{ts}.json"

s3_client = NotionBotS3Client()


def init_context(username, context):
    context.user_data['notion_client'] = NotionBotClient(username)
    if s3_client.token_exists(username):
        body = s3_client.get_token(username)
        context.user_data['notion_client'].set_link(body['value']['link'])
        context.user_data['notion_client'].set_token(body['value']['token'])
        context.user_data['notion_client'].connect()
        return ENTRY
    return SET_NOTION_LINK


def context_inited(username, context):
    try:
        _ = context.user_data['notion_client']
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
        n_uri = NotionUrl(url)
        if n_uri.parse:
            notion_url = context.user_data['notion_client'].add_row(name=n_uri.get_title(), url=n_uri.url, domain=n_uri.get_domain())
            context.bot.send_message(chat_id=update.effective_chat.id, text="Created: {}".format(notion_url))
        else:
            s3_client.put_url(context.user_data['notion_client'].user, n_uri.url)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Saved: {}".format(n_uri.url))


def start(update, context):
    update.message.reply_text("Hi, this is notion link care bot that take care of your links in notion.\n"
                              "Okay, send me the database url in like:\n"
                              "https://www.notion.so/<namespace>/<db_hash>?v=<view_hash>")
    return init_context(update.message.chat['username'], context)


def set_notion_link(update, context):
    context.user_data['notion_client'].set_link(update.message.text)
    update.message.reply_text("Good, now the hard story... send me the notion token.\n"
                              "It can be found in browser -> F12 -> Storage -> Cookies -> token_v2")
    return SET_NOTION_TOKEN


def set_notion_token(update, context):
    context.user_data['notion_client'].set_token(update.message.text)

    s3_client.put_token(user=context.user_data['notion_client'].user,
                        link=context.user_data['notion_client'].link,
                        token=context.user_data['notion_client'].token)

    context.user_data['notion_client'].connect()
    update.message.reply_text("Excellent, now you can send me the links")
    return ENTRY


def optout(update, context):
    update.message.reply_text("Not implemented yet")
    return


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
    updater = Updater(token=TGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            MessageHandler(Filters.all & (~Filters.command), links),
            CommandHandler("get", load),
            CommandHandler("start", start),
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
            ENTRY: [
                MessageHandler(Filters.all & (~Filters.command), links),
            ],
            SET_NOTION_LINK: [MessageHandler(Filters.all, set_notion_link)],
            SET_NOTION_TOKEN: [MessageHandler(Filters.all, set_notion_token)],

        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )
    dispatcher.add_handler(CommandHandler("optout", optout))
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
