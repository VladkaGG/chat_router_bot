from callbacks import run_async, Update, CallbackContext, json, InlineKeyboardButton, InlineKeyboardMarkup, os


@run_async
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello from bot, {}! Type '/help' to get information about me".format(user.username))


@run_async
def help_callback(update: Update, context: CallbackContext):
    actual_functions = {'/start': 'Just beginning a dialog with me',
                        '/add_group': 'Create new group, tell me name',
                        '/add_chat': 'Add chat to some group, tell me name and group for this chat',
                        '/add_user': 'Add user to some group, tell me name and group for this chat',
                        '/delete_group': 'Delete group, tell me name',
                        '/delete_chat': 'Delete chat from some group, tell me group',
                        # '/delete_user': 'Delete user from some group, tell me group',
                        # '/update_group': 'Update name of some group',
                        '/show_groups': 'Show all groups'}

    text = """It is actual list of possibilities:\n"""
    for name, description in actual_functions.items():
        text += "{} - {}\n".format(name, description)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


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


@run_async
def delete_group(update: Update, context: CallbackContext):
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    keyboard = list()
    end_keyboard = [InlineKeyboardButton('exit', callback_data='exit'),
                    InlineKeyboardButton('next', callback_data='next|||1')] \
        if len(all_groups) > 5 \
        else [InlineKeyboardButton('exit', callback_data='exit')]
    for group_name in list(all_groups.keys())[0:5]:
        keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
    keyboard.append(end_keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Which group do you want to delete?', reply_markup=reply_markup)
    return 1


def delete_group_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    choice = data.split('|||')[0]
    if data == 'exit':
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 2
    elif choice in ['prev', 'next']:
        page = int(data.split('|||')[1])
        with open('groups.json', 'r') as file:
            all_groups = json.loads(file.read())
        if choice == 'next':
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))],
                            [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (len(all_groups) - 5 * page > 5) else \
                [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                  InlineKeyboardButton('exit', callback_data='exit')]]
        else:
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))],
                            [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (page > 0) else \
                [[InlineKeyboardButton('exit', callback_data='exit'),
                  InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))]]
        keyboard = list()
        for group_name in list(all_groups.keys())[5 * page:5 * (page + 1)]:
            keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
        keyboard.extend(end_keyboard)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(text="Which group do you want to delete?",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup)
        return 1

    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    all_groups.pop(data)
    with open('groups.json', 'w') as file:
        file.write(json.dumps(all_groups))
    context.bot.delete_message(chat_id=query.message.chat_id,
                               message_id=query.message.message_id)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Done!")
    return 2


@run_async
def add_chat(update: Update, context: CallbackContext):
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    keyboard = list()
    end_keyboard = [InlineKeyboardButton('exit', callback_data='exit'),
                    InlineKeyboardButton('next', callback_data='next|||1')] \
        if len(all_groups) > 5 \
        else [InlineKeyboardButton('exit', callback_data='exit')]
    for group_name in list(all_groups.keys())[0:5]:
        keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
    keyboard.append(end_keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose a group:', reply_markup=reply_markup)
    return 1


@run_async
def add_chat_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    choice = data.split('|||')[0]
    if data == 'exit':
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 3
    elif choice in ['prev', 'next']:
        page = int(data.split('|||')[1])
        with open('groups.json', 'r') as file:
            all_groups = json.loads(file.read())
        if choice == 'next':
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))],
                            [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (len(all_groups) - 5 * page > 5) else \
                [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                  InlineKeyboardButton('exit', callback_data='exit')]]
        else:
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))],
                            [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (page > 0) else \
                [[InlineKeyboardButton('exit', callback_data='exit'),
                  InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))]]
        keyboard = list()
        for group_name in list(all_groups.keys())[5 * page:5 * (page + 1)]:
            keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
        keyboard.extend(end_keyboard)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(text="Please choose a group:",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup)
        return 1
    with open('choosing_group_for_adding.txt', 'w') as file:
        file.write(data)
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text='You choose {}\nWrite a name:'.format(data))
    return 2


def ending_add_chat(update: Update, context: CallbackContext):
    chat_name = update.message.text
    with open('choosing_group_for_adding.txt', 'r') as file:
        chosen_group = file.read()
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    if chat_name in all_groups[chosen_group]['chats']:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='This chat already exist in this group')
        return 3
    all_groups[chosen_group]['chats'].append(chat_name)
    with open('groups.json', 'w') as file:
        file.write(json.dumps(all_groups))
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Done!')
    os.remove('choosing_group_for_adding.txt')
    return 3


@run_async
def delete_chat(update: Update, context: CallbackContext):
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    keyboard = list()
    end_keyboard = [InlineKeyboardButton('exit', callback_data='exit'),
                    InlineKeyboardButton('next', callback_data='next|||1')] \
        if len(all_groups) > 5 \
        else [InlineKeyboardButton('exit', callback_data='exit')]
    for group_name in list(all_groups.keys())[0:5]:
        keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
    keyboard.append(end_keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose a group:', reply_markup=reply_markup)
    return 1


@run_async
def delete_chat_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    choice = data.split('|||')[0]
    if data == 'exit':
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 4
    elif choice in ['prev', 'next']:
        page = int(data.split('|||')[1])
        with open('groups.json', 'r') as file:
            all_groups = json.loads(file.read())
        if choice == 'next':
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))],
                            [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (len(all_groups) - 5 * page > 5) else \
                [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                  InlineKeyboardButton('exit', callback_data='exit')]]
        else:
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))],
                            [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (page > 0) else \
                [[InlineKeyboardButton('exit', callback_data='exit'),
                  InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))]]
        keyboard = list()
        for group_name in list(all_groups.keys())[5 * page:5 * (page + 1)]:
            keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
        keyboard.extend(end_keyboard)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(text="Choose a group:",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup)
        return 1
    with open('groups.json', 'r') as file:
        all_chats = json.loads(file.read())[choice]['chats']
    if not all_chats:
        context.bot.send_message(chat_id=query.message.chat_id,
                                 text="This group doesn't have any chats")
        return 1
    keyboard = list()
    end_keyboard = [InlineKeyboardButton('exit', callback_data='exit'),
                    InlineKeyboardButton('next', callback_data='next|||1|||{}'.format(choice))] \
        if len(all_chats) > 5 \
        else [InlineKeyboardButton('exit', callback_data='exit')]
    for chat_name in all_chats[0:5]:
        keyboard.append([InlineKeyboardButton(chat_name, callback_data='|||'.join([chat_name, choice]))])
    keyboard.append(end_keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text='You choose {}\nChoose a chat:'.format(choice),
                                  reply_markup=reply_markup)
    return 2


def ending_delete_chat(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    split_data = data.split('|||')
    if data == 'exit':
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 3
    elif split_data[0] in ['prev', 'next']:
        page = int(data.split('|||')[1])
        chosen_group = int(data.split('|||')[2])
        with open('groups.json', 'r') as file:
            all_chats = json.loads(file.read())[chosen_group]['chats']
        if split_data[0] == 'next':
            end_keyboard = [
                [InlineKeyboardButton('prev', callback_data='prev|||{}|||{}'.format(page - 1, chosen_group)),
                 InlineKeyboardButton('next', callback_data='next|||{}|||{}'.format(page + 1, chosen_group))],
                [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (len(all_chats) - 5 * page > 5) else \
                [[InlineKeyboardButton('prev', callback_data='prev|||{}|||{}'.format(page - 1, chosen_group)),
                  InlineKeyboardButton('exit', callback_data='exit')]]
        else:
            end_keyboard = [
                [InlineKeyboardButton('prev', callback_data='prev|||{}|||{}'.format(page - 1, chosen_group)),
                 InlineKeyboardButton('next', callback_data='next|||{}|||{}'.format(page + 1, chosen_group))],
                [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (page > 0) else \
                [[InlineKeyboardButton('exit', callback_data='exit'),
                  InlineKeyboardButton('next', callback_data='next|||{}|||{}'.format(page + 1, chosen_group))]]
        keyboard = list()
        for group_name in all_chats[5 * page:5 * (page + 1)]:
            keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
        keyboard.extend(end_keyboard)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(text="Choose a chat:",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup)
        return 2
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    all_groups[split_data[1]]['chats'].remove(split_data[0])
    with open('groups.json', 'w') as file:
        file.write(json.dumps(all_groups))
    context.bot.edit_message_text(text='Done!',
                                  chat_id=update.effective_chat.id,
                                  message_id=query.message.message_id)
    return 3


@run_async
def show_groups(update: Update, context: CallbackContext):
    all_groups: dict
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    keyboard = list()
    end_keyboard = [InlineKeyboardButton('exit', callback_data='exit'),
                    InlineKeyboardButton('next', callback_data='next|||1')] \
        if len(all_groups) > 5 \
        else [InlineKeyboardButton('exit', callback_data='exit')]
    for group_name in list(all_groups.keys())[0:5]:
        keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
    keyboard.append(end_keyboard)
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("It's a list of groups.\nType on group to see list of chats in chosen group",
                              reply_markup=reply_markup)
    return 1


@run_async
def show_chats(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    choice = data.split('|||')[0]
    if data == 'exit':
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 2
    elif choice in ['prev', 'next']:
        page = int(data.split('|||')[1])
        with open('groups.json', 'r') as file:
            all_groups = json.loads(file.read())
        if choice == 'next':
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page-1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page+1))],
                            [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (len(all_groups) - 5*page > 5) else \
                [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page-1)),
                  InlineKeyboardButton('exit', callback_data='exit')]]
        else:
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page-1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page+1))],
                            [InlineKeyboardButton('exit', callback_data='exit')]] \
                if (page > 0) else \
                [[InlineKeyboardButton('exit', callback_data='exit'),
                  InlineKeyboardButton('next', callback_data='next|||{}'.format(page+1))]]
        keyboard = list()
        for group_name in list(all_groups.keys())[5*page:5*(page+1)]:
            keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
        keyboard.extend(end_keyboard)
        reply_markup = InlineKeyboardMarkup(keyboard)
        context.bot.edit_message_text(text="It's a list of groups.\nType on group to see list of chats in chosen group",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup)
        return 1

    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    if not all_groups[data]['chats']:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Group {} doesn't have any chats".format(data))
        return 1
    text = "It's a list of chats for group {}:\n".format(data)
    for chat_name in all_groups[data]['chats']:
        text += '{}\n'.format(chat_name)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)
    return 1


@run_async
def error(update: Update, context: CallbackContext):
    text = "I don't know what to do with this: {}".format(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
