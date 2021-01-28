from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
import os
from telegram.ext import (
    Updater,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    Filters,
)


class Conversation:
    def __init__(self, commands=("start", "categories", "links")):
        pass
        self.conv_handler = ConversationHandler(
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
