from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup, ReplyKeyboardMarkup
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

    # @staticmethod
    # def send(update, text, reply_markup, otk):
    #     if update.message:
    #         update.message.reply_text(
    #             text=text,
    #             reply_markup=reply_markup,
    #             one_time_keyboard=otk
    #         )
    #     else:
    #         update.callback_query.edit_message_text(
    #             text=text,
    #             reply_markup=reply_markup,
    #             one_time_keyboard=otk
    #         )

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
    def start(update: Update, context: NBotContext, text='Welcome to the menu') -> None:
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
    (CHOOSE, SET) = range(2)

    def __init__(self):
        self.conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.connect, pattern='^' + str(NOTION) + '$'),
            ],
            states={
                self.CHOOSE: [
                    CallbackQueryHandler(self.get_type),
                    MessageHandler(Filters.all, self.get_type),
                ],
                self.SET: [
                    MessageHandler(Filters.all, self.set_link),
                ],
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
    def connect(update: Update, context: NBotContext) -> None:
        text = 'Choose db type to work with:'
        buttons = [
            [InlineKeyboardButton(text=t, callback_data=t) for t in context.db_container.types]
        ]

        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text, reply_markup=InlineKeyboardMarkup(buttons))

        return NBotConversationNotion.CHOOSE

    @staticmethod
    @check_context
    def get_type(update: Update, context: NBotContext) -> None:
        if update.message:
            db_type = update.message.text
        else:
            db_type = update.callback_query.data
        logger.info("{} - Got type {}".format(context.username, db_type))
        context.cv_buffer = context.db_container.get(db_type, create_if_not_exists=True)
        if not context.cv_buffer.notion_link:
            text = "Send me a notion link that associates with {}".format(db_type)
            if update.message:
                update.message.reply_text(text=text)
            else:
                update.callback_query.edit_message_text(text=text)
            return NBotConversationNotion.SET
        else:
            text = "Already have a link {}.\nBack to menu...".format(context.cv_buffer.notion_link)
            NBotConversationMain.start(update=update, context=context, text=text)
            return NBotConversationNotion.END

    @staticmethod
    @check_context
    def set_link(update: Update, context: NBotContext) -> None:
        logger.info("{} - Got Link {}".format(context.username, update.message.text))
        context.cv_buffer.notion_link = update.message.text

        NBotConversationMain.start(update=update, context=context)
        return NBotConversationNotion.END

    @staticmethod
    @check_context
    def level_up(update: Update, context: NBotContext) -> None:
        logger.info("level up!")
        NBotConversationMain.start(update=update, context=context)
        return NBotConversationNotion.END
