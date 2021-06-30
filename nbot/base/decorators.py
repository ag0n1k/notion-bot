import logging
from context import NBotContext

logger = logging.getLogger(__name__)


def check_context(func):
    def wrapper(update, context, *args, **kwargs):
        if isinstance(context, NBotContext):
            n_bot_context = context
        else:
            n_bot_context = context.user_data.get('bot_context', None)
        if not n_bot_context:
            t_user = update.message.from_user
            logger.info("No context found for the user {}".format(t_user.username))
            n_bot_context = NBotContext(username=t_user.username)
            n_bot_context.load()
            context.user_data['bot_context'] = n_bot_context
        logger.info("{} - Call the {}".format(n_bot_context.username, func.__name__))
        return func(update, n_bot_context, *args, **kwargs)
    return wrapper
