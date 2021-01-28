

def hanlder_start(update, context):
    update.message.reply_text(
        "Hi, this is notion link care bot that take care of your links in notion.\n"
        "Okay, now we have 3 actions to be done:\n"
        "  1) Choose a link database (e.g. My Links)\n"
        "  2) Add me (notion-link.care@yandex.ru) with edit permissions\n"
        "  3) Share the link to me. Like:\n"
        "https://www.notion.so/<namespace>/<db_hash>?v=<view_hash>"
    )
    # return init_context(update.message.chat['username'], context, update.effective_chat.id)
