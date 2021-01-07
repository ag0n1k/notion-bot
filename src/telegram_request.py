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

CHOOSING, REPLY, TYPING_CHOICE = range(3)
client = NotionBotClient(token=NOTION_TOKEN, link=NOTION_DB)


def start(update, context):
    reply_keyboard = [['Content', 'Link']]

    update.message.reply_text(
        'This url has content or it just link?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    context.user_data['urls'] = parse_url(update.message, parse_message)
    return CHOOSING


def echo(update, context):
    print(update.message)
    print(context.args)
    print(context.__dict__)
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


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
        notion_url = client.add_row(name=i.get_title(), url=i.url, domain=i.get_domain())
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


def main() -> None:
    updater = Updater(token=TGRAM_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.all & (~Filters.command), start)],
        states={
            CHOOSING: [
                MessageHandler(Filters.regex('^(Link)$'), link_parse),
                MessageHandler(Filters.regex('^(Content)$'), content_parse),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('^Done$'), done)],
    )

    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()