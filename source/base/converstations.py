from telegram import InlineKeyboardButton, Update, InlineKeyboardMarkup
from telegram import parsemode
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
)
from base.decorators import check_context
from context import NBotContext
import logging

logger = logging.getLogger(__name__)


class NBotConversation:
    END = ConversationHandler.END
    conversation: ConversationHandler
    (
        STORE,
        CATEGORY,
        NOTION,
        STOP,
        TYPE,
        LEVEL_ONE,
        LEVEL_TWO,
        CHOOSE_DB,
        CHOOSE_CATEGORY,
        UPDATE_CATEGORY,
        SET,
        REMOVE,
        ACTION,
        GET,
        DOMAIN
     ) = range(0, 15)

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
                logger.warning('got unknown type: {}'.format(entity.type))
        return res

    @staticmethod
    @check_context
    def level_up(update: Update, context: NBotContext) -> None:
        logger.info("{} - Level up".format(context.username))
        NBotConversationMain.start(update=update, context=context)
        return NBotConversationNotion.END

    @staticmethod
    @check_context
    def level_up(update: Update, context: NBotContext, text="Level UPPED") -> None:
        logger.info("{} - Level up".format(context.username))
        NBotConversationMain.start(update=update, context=context, text=text)
        return NBotConversationNotion.END


class NBotConversationMain(NBotConversation):
    def __init__(self):
        self.conv_notion = NBotConversationNotion()
        self.conv_category = NBotConversationCategory()
        self.conversation = ConversationHandler(
            entry_points=[
                CommandHandler('start', self.start),
                CommandHandler('configure', self.start),
                CommandHandler('process', self.store_process),
                MessageHandler(Filters.all, self.default_process),
                MessageHandler(Filters.forwarded, self.forward_process),
            ],
            states={
                self.LEVEL_ONE: [
                    self.conv_category.conversation,
                    self.conv_notion.conversation,
                    CallbackQueryHandler(self.stop, pattern='^' + str(self.END) + '$'),
                ],
                self.STOP: [
                    CallbackQueryHandler(self.stop, pattern='^' + str(self.END) + '$'),
                    MessageHandler(Filters.all, self.stop),
                ],
                self.TYPE: [
                    self.conv_category.conversation,
                ],
                self.CATEGORY: [
                    self.conv_category.conversation,
                    CallbackQueryHandler(self.stop, pattern='^' + str(self.END) + '$'),
                ],
                self.NOTION: []
            },
            fallbacks=[],
        )

    @staticmethod
    @check_context
    def start(update: Update, context: NBotContext, text='Welcome to the menu') -> None:
        buttons = [
            [
                InlineKeyboardButton(text='Update Notion', callback_data=str(NBotConversation.NOTION)),
                InlineKeyboardButton(text='Check Store', callback_data=str(NBotConversation.STORE)),
            ],
            [
                InlineKeyboardButton(text='Update Category', callback_data=str(NBotConversation.CATEGORY)),
                InlineKeyboardButton(text='Close Menu', callback_data=str(NBotConversation.END)),
            ]
        ]
        if update.message:
            update.message.reply_text(
                text=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=parsemode.constants.PARSEMODE_MARKDOWN
            )
        else:
            update.callback_query.edit_message_text(
                text=text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode=parsemode.constants.PARSEMODE_MARKDOWN
            )
        return NBotConversationMain.LEVEL_ONE

    @staticmethod
    @check_context
    def default_process(update: Update, context: NBotContext) -> None:
        res = []
        for link in context.store_difference(NBotConversationMain.get_links(update.message)):
            notion_link = context.db_container.process(link=link)
            logger.info("{} - Processed {}, result {}".format(context.username, link, notion_link))
            if not notion_link:
                res.append(link)  # save original link in store
        context.store.extend(res)
        context.save()
        update.message.reply_text(text="Processed:\n{}".format("\n".join(res)))
        return NBotConversationMain.END

    @staticmethod
    @check_context
    def store_process(update: Update, context: NBotContext) -> None:
        try:
            link = context.store.pop()
        except IndexError:
            update.message.reply_text(text="The link store is empty!")
            return NBotConversationMain.END
        update.message.reply_text(text="Choose type or send a new one of the link:\n{}".format(link))
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
                CallbackQueryHandler(self.store_start, pattern='^' + str(self.STORE) + '$'),
                CallbackQueryHandler(self.category_start, pattern='^' + str(self.CATEGORY) + '$'),
            ],
            states={
                self.UPDATE_CATEGORY: [
                    CallbackQueryHandler(self.choose_action),
                ],
                self.CHOOSE_CATEGORY: [
                    CallbackQueryHandler(self.update_category),
                    MessageHandler(Filters.all, self.choose_category),
                ],
                self.CHOOSE_DB: [
                    CallbackQueryHandler(self.update_type),
                    MessageHandler(Filters.all, self.create_type),
                ],
                self.LEVEL_ONE: [
                    CallbackQueryHandler(self.stop, pattern='^' + str(self.END) + '$'),
                ],
                self.ACTION: [
                    CallbackQueryHandler(self.print_domains, pattern='^' + str(self.GET) + '$'),
                    CallbackQueryHandler(self.stop, pattern='^' + str(self.REMOVE) + '$'),
                    CallbackQueryHandler(self.stop, pattern='^' + str(self.DOMAIN) + '$'),
                    CallbackQueryHandler(self.stop, pattern='^' + str(self.END) + '$'),
                ],
            },
            map_to_parent={
                # Return to second level menu
                self.END: self.LEVEL_ONE,
            },
            fallbacks=[CallbackQueryHandler(self.level_up, pattern='^' + str(self.END) + '$')]
        )

    @staticmethod
    @check_context
    def store_start(update: Update, context: NBotContext) -> None:
        try:
            link = context.store.pop()
        except IndexError:
            update.callback_query.edit_message_text(text="The link store is empty!")
            return NBotConversationMain.END
        context.link_buffer = link
        text = "Choose type or send a new one of the link:\n{}".format(context.link_buffer)
        buttons = [
            [InlineKeyboardButton(text=t, callback_data=t) for t in context.db_container.get_categories()]
        ]

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))

        return NBotConversation.CHOOSE_CATEGORY

    @staticmethod
    @check_context
    def choose_action(update: Update, context: NBotContext) -> None:
        context.category_buffer = update.callback_query.data
        buttons = [[
            InlineKeyboardButton(text="Print", callback_data=str(NBotConversation.GET)),
            InlineKeyboardButton(text="Remove", callback_data=str(NBotConversation.REMOVE)),
            InlineKeyboardButton(text="Domains", callback_data=str(NBotConversation.DOMAIN)),
            InlineKeyboardButton(text="Close", callback_data=str(NBotConversation.END)),
        ]]
        update.callback_query.edit_message_text(text="Choose action", reply_markup=InlineKeyboardMarkup(buttons))

        return NBotConversation.ACTION

    @staticmethod
    @check_context
    def choose_domain(update: Update, context: NBotContext) -> None:
        text = "Choose action"
        typ = context.db_container.get_type_by_category(context.category_buffer)
        buttons = [
            [InlineKeyboardButton(text=d, callback_data=d) for d in typ.get_domains(context.category_buffer)]
        ]
        update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
        return NBotConversation.CHOOSE_CATEGORY

    @staticmethod
    @check_context
    def choose_domain_action(update: Update, context: NBotContext) -> None:
        text = "Choose action"
        typ = context.db_container.get_type_by_category(context.category_buffer)
        buttons = [
            [InlineKeyboardButton(text=d, callback_data=d) for d in typ.get_domains(context.category_buffer)]
        ]
        update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
        return NBotConversation.CHOOSE_CATEGORY

    @staticmethod
    @check_context
    def print_domains(update: Update, context: NBotContext) -> None:
        typ = context.db_container.get_type_by_category(context.category_buffer)
        NBotConversationMain.start(
            update=update, context=context,
            text="Domains:\n{}\nBack to menu...".format(typ.get_domains(context.category_buffer))
        )
        return NBotConversation.END


    @staticmethod
    @check_context
    def category_start(update: Update, context: NBotContext) -> None:
        text = "Choose category"
        buttons = [
            [InlineKeyboardButton(text=t, callback_data=t) for t in context.db_container.get_categories()]
        ]

        update.callback_query.answer()
        update.callback_query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))

        return NBotConversation.UPDATE_CATEGORY


    @staticmethod
    @check_context
    def create_type(update: Update, context: NBotContext) -> None:
        if update.message:
            db_type = update.message.text
        else:
            db_type = update.callback_query.data
        logger.info("{} - create type {}".format(context.username, db_type))
        context.db_container.update_categories(
            db_type=db_type, category=context.category_buffer, links=[context.link_buffer])
        NBotConversationMain.start(
            update=update, context=context,
            text="Link {}\nCategory={}, Type={}\nBack to menu...".format(context.link_buffer,
                                                                         context.category_buffer, db_type)
        )
        context.link_buffer = ""
        context.category_buffer = ""
        return NBotConversation.END

    @staticmethod
    @check_context
    def update_category(update: Update, context: NBotContext) -> None:
        logger.info("{} - update category {}".format(context.username, update.callback_query.data))
        context.category_buffer = update.callback_query.data
        db_type = context.db_container.get_type_by_category(update.callback_query.data)
        update.callback_query.data = db_type.db_type
        return NBotConversationCategory.update_type(update=update, context=context)

    @staticmethod
    @check_context
    def update_type(update: Update, context: NBotContext) -> None:
        logger.info("{} - update type {}".format(context.username, update.callback_query.data))
        logger.info("{} - update type context {}".format(context.username, context.__dict__))
        context.db_container.update_categories(
            db_type=update.callback_query.data, category=context.category_buffer, links=[context.link_buffer]
        )
        NBotConversationMain.start(update=update, context=context,
                                   text="The link {} saved with\ntype = *{}*,category = *{}*.\n"
                                        "Now *re-send* the link to me.".format(context.link_buffer,
                                                                               context.category_buffer,
                                                                               update.callback_query.data),
                                   )
        context.category_buffer = ""
        context.link_buffer = ""
        context.save()
        return NBotConversation.END

    @staticmethod
    @check_context
    def choose_category(update: Update, context: NBotContext) -> None:
        logger.info("{} - choose type {}".format(context.username, update.message.text))
        context.category_buffer = update.message.text
        return NBotConversationNotion.connect(update=update, context=context)


class NBotConversationNotion(NBotConversation):
    def __init__(self):
        self.conversation = ConversationHandler(
            entry_points=[
                CallbackQueryHandler(self.connect, pattern='^' + str(self.NOTION) + '$'),
            ],
            states={
                self.CHOOSE_DB: [
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
        text = 'Choose db type:'
        buttons = [
            [InlineKeyboardButton(text=t, callback_data=t) for t in context.db_container.types]
        ]
        if update.message:
            update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            update.callback_query.answer()
            update.callback_query.edit_message_text(
                text=text, reply_markup=InlineKeyboardMarkup(buttons))
        return NBotConversationNotion.CHOOSE_DB

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
