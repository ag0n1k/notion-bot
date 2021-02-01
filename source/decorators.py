import logging
from context import NBotContext

logger = logging.getLogger(__name__)


def check_context(func):
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
            bot_context.user_data['bot_context'] = context

        logger.info("{} - Call the {}".format(context.username, func.__name__))
        return func(update, context, *args, **kwargs)
    return wrapper
