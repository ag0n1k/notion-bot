from helpers.decorators import init_context


@init_context
def remove_category(update, context):
    if not context_inited(update.message.chat['username'], context, update.effective_chat.id):
        update.message.reply_text("No Notion information found. Please use start command.")
        return START

    update.message.reply_text(
        "Choose the category to remove.",
        reply_markup=ReplyKeyboardMarkup([context.user_data['bot_context'].get_categories()], one_time_keyboard=True)
    )
    return RM_CATEGORY
