from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext,
)
from base.constants import *
from base.decorators import check_context
from context import NBotContext
import logging

logger = logging.getLogger(__name__)


class NBotConversation:
    END = ConversationHandler.END
    conversation: ConversationHandler
    (LEVEL_ONE, LEVEL_TWO) = map(chr, range(0, 2))

    @staticmethod
    def start(update: Update, context: NBotContext) -> None:
        raise NotImplementedError()

    @staticmethod
    @check_context
    def stop(update: Update, context: NBotContext) -> None:
        """End Conversation by command."""
        text = 'Okay, bye.'
        if update.message:
            update.message.reply_text(text=text)
        else:
            update.callback_query.edit_message_text(text=text)
        return NBotConversation.END


class NBotConversationMain(NBotConversation):
    def __init__(self):
        self.conv_notion = NBotConversationNotion()
        self.conv_category = NBotConversationCategory()
        self.conversation = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start),
                CommandHandler('configure', self.start),
                MessageHandler(Filters.all, self.process),
            ],
            states={
                self.LEVEL_ONE: [
                    self.conv_category.conversation,
                    self.conv_notion.conversation,
                    CallbackQueryHandler(self.stop, pattern='^' + str(ConversationHandler.END) + '$'),

                ],
                CATEGORY: [],
                NOTION: []
            },
            fallbacks=[]
        )

    @staticmethod
    @check_context
    def start(update: Update, context: NBotContext) -> None:
        text = 'Welcome to the menu'
        buttons = [[
            InlineKeyboardButton(text='Notion', callback_data=str(NOTION)),
            InlineKeyboardButton(text='Category', callback_data=str(CATEGORY)),
            InlineKeyboardButton(text='Done', callback_data=str(ConversationHandler.END)),
        ]]
        if update.message:
            update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))

        return NBotConversationMain.LEVEL_ONE

    @staticmethod
    @check_context
    def process(update: Update, context: NBotContext) -> None:
        update.message.reply_text(text=update.message.text + " " + str(context.__dict__))
        return NBotConversationMain.END


class NBotConversationCategory(NBotConversation):
    def __init__(self):
        self.conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.stop, pattern='^' + str(CATEGORY) + '$'),
            ],
            states={
                self.LEVEL_ONE: [
                    CallbackQueryHandler(self.stop, pattern='^' + str(ConversationHandler.END) + '$'),
                ],
            },
            map_to_parent={
                # Return to second level menu
                self.END: self.LEVEL_ONE,
            },
            fallbacks=[]
        )

    @staticmethod
    @check_context
    def start(update: Update, context: NBotContext) -> None:
        update.message.reply_text(text='text')
        return NBotConversationCategory.END


class NBotConversationNotion(NBotConversation):
    def __init__(self):
        self.conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.start, pattern='^' + str(NOTION) + '$'),
            ],
            states={
                self.LEVEL_ONE: [
                    CallbackQueryHandler(self.stop, pattern='^' + str(ConversationHandler.END) + '$'),
                ],
            },
            map_to_parent={
                # Return to second level menu
                self.END: self.LEVEL_ONE,
            },
            fallbacks=[
                CallbackQueryHandler(self.level_up, pattern='^' + str(self.END) + '$'),
            ]
        )

    @staticmethod
    @check_context
    def start(update: Update, context: NBotContext) -> None:
        text = 'Okay, bye.'
        if update.message:
            update.message.reply_text(text=text)
        else:
            update.callback_query.edit_message_text(text=text)
        NBotConversationMain.start(update=update, context=context)
        return NBotConversation.END

    @staticmethod
    @check_context
    def level_up(update: Update, context: NBotContext) -> None:
        logger.info("level up!")
        NBotConversationMain.start(update=update, context=context)
        return NBotConversationNotion.END
