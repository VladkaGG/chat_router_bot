from callbacks import run_async, Update, CallbackContext, json
from callbacks.Buttons import Markup
from telegram_client.adding import add_user
from work_with_db import DbModel


@run_async
def start(update: Update, context: CallbackContext):
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello from bot, {}! Type '/help' to get information about me".format(user.username))


@run_async
def help_callback(update: Update, context: CallbackContext):
    actual_functions = {'/start': 'Just saying hello)',
                        '/add_group': 'Create new group',
                        '/add_chat': 'Add chat to some group',
                        '/add_user': 'Add user to some group',
                        '/delete_group': 'Delete group',
                        '/delete_chat': 'Delete chat from some group',
                        # '/delete_user': 'Delete user from some group, tell me group',
                        # '/update_group': 'Update name of some group',
                        '/show_groups': 'Show all groups'}

    text = """It is actual list of possibilities:\n"""
    for name, description in actual_functions.items():
        text += "{} - {}\n".format(name, description)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


class DeleteGroup:
    all_groups = []
    parent_name = None
    choosing_group_for_adding = None

@run_async
def add_group(update: Update, context: CallbackContext):
    db = DbModel()
    DeleteGroup.all_groups = db.show_first_groups()
    if not DeleteGroup.all_groups:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Write name of group if you want to add it")
        return 1
    all_groups = DeleteGroup.all_groups
    reply_markup = Markup(all_groups)
    update.message.reply_text('Tap on name to go on next level or write name of group if you want to add it',
                              reply_markup=reply_markup.return_keyboard())
    return 1


def add_group_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    db = DbModel()
    choice = data.split('|||')[0]
    if data == 'exit':
        DeleteGroup.all_groups = []
        DeleteGroup.parent_name = None
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 2
    elif choice == 'back':
        parent_name = db.show_parent_name(DeleteGroup.parent_name)
        if not parent_name:
            DeleteGroup.parent_name = None
            DeleteGroup.all_groups = db.show_first_groups()
        else:
            DeleteGroup.parent_name = parent_name[0]
            DeleteGroup.all_groups = db.show_groups(DeleteGroup.parent_name)
        reply_markup = Markup(DeleteGroup.all_groups)
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    elif choice in ['prev', 'next']:
        page = int(data.split('|||')[1])
        reply_markup = Markup(DeleteGroup.all_groups, page)
        if choice == 'next':
            reply_markup.next()
            if DeleteGroup.parent_name is not None:
                reply_markup.add_back()
        else:
            reply_markup.prev()
            if DeleteGroup.parent_name is not None:
                reply_markup.add_back()
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    DeleteGroup.parent_name = data
    DeleteGroup.all_groups = db.show_groups(DeleteGroup.parent_name)
    if not DeleteGroup.all_groups:
        reply_markup = Markup(DeleteGroup.all_groups)
        reply_markup.add_back()
        context.bot.edit_message_text(text="Write name of group if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    else:
        reply_markup = Markup(DeleteGroup.all_groups)
        reply_markup.add_back()
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1


def ending_add_group(update: Update, context: CallbackContext):
    db = DbModel()
    group_name = update.message.text
    if group_name in DeleteGroup.all_groups:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='This group already exists')
        return 1
    else:
        if DeleteGroup.parent_name is not None:
            db.add_group(group_name, DeleteGroup.parent_name)
        else:
            db.add_first_group(group_name)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Done!')
        DeleteGroup.all_groups = []
        DeleteGroup.parent_name = None
        return 2


@run_async
def delete_group(update: Update, context: CallbackContext):
    db = DbModel()
    DeleteGroup.all_groups = db.show_first_groups()
    if not DeleteGroup.all_groups:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have any groups "
                                                                        "text /add_group first!")
        DeleteGroup.all_groups = []
        return 2
    all_groups = DeleteGroup.all_groups
    reply_markup = Markup(all_groups)
    update.message.reply_text('Tap on name to go on next level or write name of group if you want to delete it',
                              reply_markup=reply_markup.return_keyboard())
    return 1


def delete_group_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    db = DbModel()
    choice = data.split('|||')[0]
    if data == 'exit':
        DeleteGroup.all_groups = []
        DeleteGroup.parent_name = None
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 2
    elif choice == 'back':
        parent_name = db.show_parent_name(DeleteGroup.parent_name)
        if not parent_name:
            DeleteGroup.parent_name = None
            DeleteGroup.all_groups = db.show_first_groups()
        else:
            DeleteGroup.parent_name = parent_name[0]
            DeleteGroup.all_groups = db.show_groups(DeleteGroup.parent_name)
        reply_markup = Markup(DeleteGroup.all_groups)
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to delete it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    elif choice in ['prev', 'next']:
        page = int(data.split('|||')[1])
        reply_markup = Markup(DeleteGroup.all_groups, page)
        if choice == 'next':
            reply_markup.next()
            if DeleteGroup.parent_name is not None:
                reply_markup.add_back()
        else:
            reply_markup.prev()
            if DeleteGroup.parent_name is not None:
                reply_markup.add_back()
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to delete it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    DeleteGroup.all_groups = db.show_groups(data)
    if not DeleteGroup.all_groups:
        DeleteGroup.all_groups = db.show_groups(DeleteGroup.parent_name)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='There is no groups here')
        return 1
    else:
        DeleteGroup.parent_name = data
        DeleteGroup.all_groups = db.show_groups(DeleteGroup.parent_name)
        reply_markup = Markup(DeleteGroup.all_groups)
        reply_markup.add_back()
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to delete it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1


def ending_delete_group(update: Update, context: CallbackContext):
    db = DbModel()
    group_name = update.message.text
    if group_name in DeleteGroup.all_groups:
        db.delete_group(group_name)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Done!')
        DeleteGroup.all_groups = []
        DeleteGroup.parent_name = None
        return 2
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='There is no group with this name on current level')
        return 1


class AddChat:
    all_groups: dict = {}
    choosing_group_for_adding = ''


@run_async
def add_chat(update: Update, context: CallbackContext):
    db = DbModel()
    DeleteGroup.all_groups = db.show_first_groups()
    if not DeleteGroup.all_groups:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have any groups "
                                                                        "text /add_group first!")
        DeleteGroup.all_groups = []
        return 3
    all_groups = DeleteGroup.all_groups
    reply_markup = Markup(all_groups)
    update.message.reply_text('Tap on name to go on next level or write name of group if you want to choose it',
                              reply_markup=reply_markup.return_keyboard())
    return 1


def add_chat_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    db = DbModel()
    choice = data.split('|||')[0]
    if data == 'exit':
        DeleteGroup.all_groups = []
        DeleteGroup.parent_name = None
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 2
    elif choice == 'back':
        parent_name = db.show_parent_name(DeleteGroup.parent_name)
        if not parent_name:
            DeleteGroup.parent_name = None
            DeleteGroup.all_groups = db.show_first_groups()
        else:
            DeleteGroup.parent_name = parent_name[0]
            DeleteGroup.all_groups = db.show_groups(DeleteGroup.parent_name)
        reply_markup = Markup(DeleteGroup.all_groups)
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    elif choice in ['prev', 'next']:
        page = int(data.split('|||')[1])
        reply_markup = Markup(DeleteGroup.all_groups, page)
        if choice == 'next':
            reply_markup.next()
            if DeleteGroup.parent_name is not None:
                reply_markup.add_back()
        else:
            reply_markup.prev()
            if DeleteGroup.parent_name is not None:
                reply_markup.add_back()
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    DeleteGroup.parent_name = data
    DeleteGroup.all_groups = db.show_groups(DeleteGroup.parent_name)
    if not DeleteGroup.all_groups:
        reply_markup = Markup(DeleteGroup.all_groups)
        reply_markup.add_back()
        context.bot.edit_message_text(text="Write name of group if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    else:
        reply_markup = Markup(DeleteGroup.all_groups)
        reply_markup.add_back()
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1


def ending_add_chat_button(update: Update, context: CallbackContext):
    group_name = update.message.text
    if group_name in DeleteGroup.all_groups:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You choose {}\nWrite a name:'.format(group_name))
        DeleteGroup.choosing_group_for_adding = group_name
        DeleteGroup.all_groups = []
        DeleteGroup.parent_name = None
        return 2
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='There is no group with this name on current level')
        return 1


def ending_add_chat(update: Update, context: CallbackContext):
    chat_name = update.message.text
    chosen_group = DeleteGroup.choosing_group_for_adding
    db = DbModel()
    if chat_name in db.show_chats(chosen_group):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='This chat already exists in this group')
        return 3
    db.add_chat(chat_name, chosen_group)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Done!')
    DeleteGroup.choosing_group_for_adding = None
    return 3


def ending_add_user(update: Update, context: CallbackContext):
    username = update.message.text
    chosen_group = AddChat.choosing_group_for_adding
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
    AddChat.choosing_group_for_adding = ''
    return 3


class DeleteChat:
    all_groups = {}
    choice_group: str = ''
    choice: list = []


@run_async
def delete_chat(update: Update, context: CallbackContext):
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
        DeleteChat.all_groups = all_groups
    reply_markup = Markup(all_groups)
    update.message.reply_text('Please choose a group:', reply_markup=reply_markup.return_keyboard())
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
        reply_markup = Markup(DeleteChat.all_groups, page)
        reply_markup.next() if choice == 'next' else reply_markup.prev()
        context.bot.edit_message_text(text="Choose a group:",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    DeleteChat.choice_group = choice
    DeleteChat.choice = DeleteChat.all_groups[choice]['chats']
    if not DeleteChat.choice:
        context.bot.send_message(chat_id=query.message.chat_id,
                                 text="This group doesn't have any chats")
        return 1
    reply_markup = Markup(DeleteChat.choice)
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text='You choose {}\nChoose a chat:'.format(choice),
                                  reply_markup=reply_markup.return_keyboard())
    return 2


def ending_delete_chat(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    choice = data.split('|||')[0]
    if data == 'exit':
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 3
    elif choice in ['prev', 'next']:
        page = int(data.split('|||')[1])
        reply_markup = Markup(DeleteChat.choice, page)
        reply_markup.next() if choice[0] == 'next' else reply_markup.prev()
        context.bot.edit_message_text(text="Choose a chat:",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 2

    DeleteChat.all_groups[DeleteChat.choice_group]['chats'].remove(choice)
    with open('groups.json', 'w') as file:
        file.write(json.dumps(DeleteChat.all_groups))
    DeleteChat.all_groups = {}
    DeleteChat.choice_group = ''
    DeleteChat.choice = []
    context.bot.edit_message_text(text='Done!',
                                  chat_id=update.effective_chat.id,
                                  message_id=query.message.message_id)
    return 3


@run_async
def show_groups(update: Update, context: CallbackContext):
    all_groups: dict
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    reply_markup = Markup(all_groups)
    update.message.reply_text("It's a list of groups.\nType on group to see list of chats in chosen group",
                              reply_markup=reply_markup.return_keyboard())
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
        reply_markup = Markup(all_groups, page)
        reply_markup.next() if choice == 'next' else reply_markup.prev()
        context.bot.edit_message_text(text="It's a list of groups.\nType on group to see list of chats in chosen group",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
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
