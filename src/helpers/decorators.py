import logging
from base.context import NBotContext
from handlers.entry import start

logger = logging.getLogger(__name__)


def init_context(func):
    def wrapper(update, bot_context, *args, **kwargs):
        if update.callback_query:
            update.message = update.callback_query.message
            update.message.from_user = update.callback_query.from_user

        context = bot_context.user_data.get('bot_context', None)
        if not context:
            t_user = update.message.from_user
            logger.info("No context found for the user {}".format(t_user.username))
            context = NBotContext(username=t_user.username)
            context.load()
            context.connect()
            bot_context.user_data['bot_context'] = context
        if not context.connected:
            logger.info("Connection is lost for the user {}".format(context.username))
            update.message.reply_text("Init the bot!")
            return start(update, context, *args, **kwargs)
        logger.info("{} - Call the {}".format(context.username, func.__name__))
        return func(update, context, *args, **kwargs)

    return wrapper
