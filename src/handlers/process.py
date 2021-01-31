from base.context import NBotContext
from helpers.decorators import init_context
from helpers.message import next_choose
from base.constants import *
import logging

logger = logging.getLogger(__name__)


@init_context
def next_or_stop(update, context: NBotContext):
    context.clear()
    next_choose(update, context)
    return CHOOSING
