from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram import MessageEntity
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
from utils import get_domain
import logging

logger = logging.getLogger(__name__)


class NBotConversation:
    END = ConversationHandler.END
    conversation: ConversationHandler
    (STOP, LEVEL_ONE, LEVEL_TWO) = map(chr, range(0, 3))

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

    @staticmethod
    def get_links(message):
        return NBotConversation.parse_links(entities=message.caption_entities, text=message.caption) \
            if message.caption \
            else NBotConversation.parse_links(entities=message.entities, text=message.text)

    @staticmethod
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


class NBotConversationMain(NBotConversation):
    def __init__(self):
        self.conv_notion = NBotConversationNotion()
        self.conv_category = NBotConversationCategory()
        self.conversation = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start),
                CommandHandler('configure', self.start),
                MessageHandler(Filters.all, self.default_process),
                MessageHandler(Filters.forwarded, self.forward_process),
            ],
            states={
                self.LEVEL_ONE: [
                    self.conv_category.conversation,
                    self.conv_notion.conversation,
                    CallbackQueryHandler(self.stop, pattern='^' + str(ConversationHandler.END) + '$'),
                ],
                self.STOP: [
                    CallbackQueryHandler(self.stop, pattern='^' + str(ConversationHandler.END) + '$'),
                    MessageHandler(Filters.all, self.stop),
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
            InlineKeyboardButton(text='Done', callback_data=str(ConversationHandler.END)),
        ]]
        if update.message:
            update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))

        return NBotConversationMain.LEVEL_ONE

    @staticmethod
    @check_context
    def default_process(update: Update, context: NBotContext) -> None:
        res = []
        for link in context.store_difference(NBotConversationMain.get_links(update.message)):
            notion_link = context.db_container.process(domain=get_domain(link))
            res.append(notion_link) if notion_link else link  # if saved: link to notion, else original link
        context.store.extend(res)
        update.message.reply_text(text="Processed:\n{}".format("\n".join(res)))
        return NBotConversationMain.STOP

    @staticmethod
    @check_context
    def forward_process(update: Update, context: NBotContext) -> None:
        update.message.reply_text(
            text="Got '''\n" + update.message.text + "'''\nIt's interesting. But not implemented...")
        return NBotConversationMain.STOP


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
    (CHOOSE, SET, REMOVE, ACTION, GET) = range(5)

    def __init__(self):
        self.conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.connect, pattern='^' + str(NOTION) + '$'),
            ],
            states={
                self.CHOOSE: [
                    CallbackQueryHandler(self.get_action),
                    MessageHandler(Filters.all, self.get_type),
                ],
                self.ACTION: [
                    CallbackQueryHandler(self.remove, pattern='^' + str(self.REMOVE) + '$'),
                    CallbackQueryHandler(self.typing_link, pattern='^' + str(self.SET) + '$'),
                    CallbackQueryHandler(self.get_link, pattern='^' + str(self.GET) + '$'),
                ],
                self.SET: [
                    MessageHandler(Filters.all, self.set_link),
                ],
                self.REMOVE: [
                    MessageHandler(Filters.all, self.remove),
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
    def get_action(update: Update, context: NBotContext) -> None:
        if update.message:
            db_type = update.message.text
        else:
            db_type = update.callback_query.data
        context.cv_buffer = context.db_container.get(db_type)
        text = 'Set or Remove {}'.format(context.cv_buffer.db_type)
        buttons = [[
            InlineKeyboardButton(text="Get", callback_data=str(NBotConversationNotion.GET)),
            InlineKeyboardButton(text="Set", callback_data=str(NBotConversationNotion.SET)),
            InlineKeyboardButton(text="Remove", callback_data=str(NBotConversationNotion.REMOVE))
        ]]

        update.callback_query.edit_message_text(
            text=text, reply_markup=InlineKeyboardMarkup(buttons))

        return NBotConversationNotion.ACTION

    @staticmethod
    @check_context
    def get_type(update: Update, context: NBotContext) -> None:
        db_type = update.message.text
        logger.info("{} - Got type {}".format(context.username, db_type))
        context.cv_buffer = context.db_container.get(db_type, create_if_not_exists=True)
        return NBotConversationNotion.typing_link(update=update, context=context)

    @staticmethod
    @check_context
    def typing_link(update: Update, context: NBotContext) -> None:
        text = "Send me a notion link that associates with {}".format(context.cv_buffer.db_type)
        if update.message:
            update.message.reply_text(text=text)
        else:
            update.callback_query.answer()
            update.callback_query.edit_message_text(text=text)
        return NBotConversationNotion.SET

    @staticmethod
    @check_context
    def get_link(update: Update, context: NBotContext) -> None:
        text = "The type {} with {}.\nBack in menu...".format(context.cv_buffer.db_type,
                                                              context.cv_buffer.notion_link)
        NBotConversationMain.start(update=update, context=context, text=text)

        return NBotConversationNotion.END

    @staticmethod
    @check_context
    def set_link(update: Update, context: NBotContext) -> None:
        logger.info("{} - Got Link {}".format(context.username, update.message.text))
        context.cv_buffer.notion_link = update.message.text
        del context.cv_buffer
        context.save()

        NBotConversationMain.start(update=update, context=context)
        return NBotConversationNotion.END

    @staticmethod
    @check_context
    def remove(update: Update, context: NBotContext) -> None:
        logger.info("{} - Removing {}".format(context.username, context.cv_buffer.db_type))
        context.db_container.remove(context.cv_buffer.db_type)
        context.save()

        NBotConversationMain.start(update=update, context=context)
        return NBotConversationNotion.END

    @staticmethod
    @check_context
    def level_up(update: Update, context: NBotContext) -> None:
        logger.info("level up!")
        NBotConversationMain.start(update=update, context=context)
        return NBotConversationNotion.END
