import logging
from context import NBotContext
from helpers.constants import *

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
            logger.info("Connection established for the user {}".format(context.username))
            bot_context.user_data['bot_context'] = context
        if not context.connected:
            return START
        return func(update, context, *args, **kwargs)

    return wrapper
