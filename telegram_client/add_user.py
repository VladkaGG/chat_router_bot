from callbacks import Update, CallbackContext, json, os, InlineKeyboardButton, InlineKeyboardMarkup, run_async
from .adding import add_user


def ending_add_user(update: Update, context: CallbackContext):
    username = update.message.text
    with open('choosing_group_for_adding.txt', 'r') as file:
        chosen_group = file.read()
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    all_chats = all_groups[chosen_group]['chats']
    del all_groups
    if not all_chats:
        context.bot.send_message(chat_id=update.effective_chat.id, text="This group doesn't have any chats")
        return 3
    for chat in all_chats:
        result = add_user(chat, username)
        context.bot.send_message(chat_id=update.effective_chat.id, text=result)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Done!')
    os.remove('choosing_group_for_adding.txt')
    return 3
