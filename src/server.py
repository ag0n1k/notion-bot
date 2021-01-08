from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)
from notion_link import NotionBotClient, NotionUrl
from settings import (
    NOTION_TOKEN,
    NOTION_DB,
    TGRAM_TOKEN,
    SAVE_FILE
)

CHOOSING, ENTRY, TYPING_CHOICE, SET_NOTION_LINK, SET_NOTION_TOKEN = range(5)


def links(update, context):
    with open(SAVE_FILE, 'a') as f:
        for i in parse_url(update.message, parse_message):
            if i.parse:
                notion_url = context.user_data['notion_client'].add_row(name=i.get_title(), url=i.url, domain=i.get_domain())
                context.bot.send_message(chat_id=update.effective_chat.id, text="Created: {}".format(notion_url))
            else:
                f.write(i.url + '\n')
                context.bot.send_message(chat_id=update.effective_chat.id, text="Saved: {}".format(i.url))


def start(update, context):
    update.message.reply_text("Hi, this is notion link care bot that take care of your links in notion.\n"
                              "Okay, send me the database url in like:\n"
                              "https://www.notion.so/<namespace>/<db_hash>?v=<view_hash>")
    return SET_NOTION_LINK


def set_notion_link(update, context):
    context.user_data['notion_link'] = update.message.text

    update.message.reply_text("Good, now the hard story... send me the notion token.\n"
                              "It can be found in browser -> F12 -> Storage -> Cookies -> token_v2")

    return SET_NOTION_TOKEN


def set_notion_token(update, context):
    context.user_data['notion_token'] = update.message.text

    client = NotionBotClient(token=context.user_data['notion_token'], link=context.user_data['notion_link'])
    context.user_data['notion_client'] = client

    update.message.reply_text("Excellent, now you can send me the links")
    return ENTRY


def optout(update, context):
    update.message.reply_text("Not implemented yet")
    return


def de_start(update, context):
    reply_keyboard = [['Content', 'Link']]

    update.message.reply_text(
        'This url has content or it just link?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    context.user_data['urls'] = parse_url(update.message, parse_message)
    return CHOOSING


def parse_message(message):
    """
    Telegram allows to post text with picture in different way: caption with caption entities.
    By default received the text and entities.
    :param message: the telegram message
    :return: real text and entities
    """
    if message.caption:
        return message.caption, message.caption_entities
    return message.text, message.entities


def parse_url(message, func):
    """
    Get the urls from the message
    :param message: the original telegram message
    :param func: the function to parse the message onto text and entities
    :return: list of NotionUrl objects
    """
    text, entities = func(message)
    result = set()
    for entity in entities:
        if entity.type == 'text_link':
            result.add(NotionUrl(entity.url))
        elif entity.type == 'url':
            result.add(NotionUrl(text[entity.offset:entity.offset+entity.length]))
        else:
            print('got unknown type: ', entity.type)
    return list(result)


def link_parse(update, context):
    print('link logic')
    print(context.user_data)
    for i in context.user_data['urls']:
        notion_url = context.user_data['notion_client'].add_row(name=i.get_title(), url=i.url, domain=i.get_domain())
        context.bot.send_message(chat_id=update.effective_chat.id, text="Created: {}".format(notion_url))

    return ConversationHandler.END


def content_parse(update, context):
    print('Content logic')
    print(context.user_data)
    with open(SAVE_FILE, 'a') as f:
        for i in context.user_data['urls']:
            f.write(i.url)
            context.bot.send_message(chat_id=update.effective_chat.id, text="Saved: {}".format(i.url))
    return ConversationHandler.END


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
            ENTRY: [
                MessageHandler(Filters.all & (~Filters.command), links),
            ],
            CHOOSING: [
                MessageHandler(Filters.regex('^(Link)$'), link_parse),
                MessageHandler(Filters.regex('^(Content)$'), content_parse),
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