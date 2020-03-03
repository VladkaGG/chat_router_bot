from callbacks import Update, CallbackContext, json


def add_group(update: Update, context: CallbackContext):
    data = update.message.text.split(' ')
    if not data or (len(data) == 1 and data[0] == '/add_group'):
        context.bot.send_message(chat_id=update.effective_chat.id, text='Write a group name:')
        return 0
    group_name = ' '.join(data[1:]) if data[0] == '/add_group' else ' '.join(data)
    if ' ' in group_name:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='All spaces will be replaced by _')
        group_name = group_name.replace(' ', '_')
    with open('groups.json', 'r') as file:
        all_groups: dict = json.loads(file.read())
    if group_name in list(all_groups.keys()):
        context.bot.send_message(chat_id=update.effective_chat.id, text='This group already exists')
        return 1
    all_groups[group_name] = {'groups': {}, 'chats': []}
    with open('groups.json', 'w') as file:
        file.write(json.dumps(all_groups))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Done!")
    return 1
