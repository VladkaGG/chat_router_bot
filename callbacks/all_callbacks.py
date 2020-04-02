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
    message_id = None
    choice = None


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
    DeleteGroup.message_id = query.message.message_id
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
        context.bot.delete_message(chat_id=update.effective_chat.id,
                                   message_id=DeleteGroup.message_id)
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
    DeleteGroup.message_id = query.message.message_id
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
    print(data)
    if not DeleteGroup.all_groups:
        if DeleteGroup.parent_name is None:
            DeleteGroup.all_groups = db.show_first_groups()
        else:
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
        context.bot.delete_message(chat_id=update.effective_chat.id,
                                   message_id=DeleteGroup.message_id)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Done!')
        DeleteGroup.all_groups = []
        DeleteGroup.parent_name = None
        return 2
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='There is no group with this name on current level')
        return 1


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
    update.message.reply_text('Tap on name to go on next level or write name of chat if you want to add it',
                              reply_markup=reply_markup.return_keyboard())
    return 1


def add_chat_button(update: Update, context: CallbackContext):
    query = update.callback_query
    DeleteGroup.message_id = query.message.message_id
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
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of chat "
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
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of chat "
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
        context.bot.edit_message_text(text="Write name of chat if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    else:
        reply_markup = Markup(DeleteGroup.all_groups)
        reply_markup.add_back()
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of chat "
                                           "if you want to add it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1


def ending_add_chat(update: Update, context: CallbackContext):
    chat_name = update.message.text
    chosen_group = DeleteGroup.parent_name
    print(chosen_group)
    db = DbModel()
    if chosen_group is None:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='Choose group first')
        return 1
    if chat_name in db.show_chats(chosen_group):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='This chat already exists in this group')
        return 1
    db.add_chat(chosen_group, chat_name)
    context.bot.delete_message(chat_id=update.effective_chat.id,
                               message_id=DeleteGroup.message_id)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Done!')
    DeleteGroup.all_groups = []
    DeleteGroup.parent_name = None
    return 2


@run_async
def show_groups(update: Update, context: CallbackContext):
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


@run_async
def show_groups_button(update: Update, context: CallbackContext):
    query = update.callback_query
    DeleteGroup.message_id = query.message.message_id
    data = query.data
    db = DbModel()
    choice = data.split('|||')[0]
    if data == 'exit':
        DeleteGroup.all_groups = []
        DeleteGroup.parent_name = None
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 3
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
                                           "if you want to choose it",
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
                                           "if you want to choose it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1
    DeleteGroup.all_groups = db.show_groups(data)
    if not DeleteGroup.all_groups:
        if DeleteGroup.parent_name is None:
            DeleteGroup.all_groups = db.show_first_groups()
        else:
            DeleteGroup.all_groups = db.show_groups(DeleteGroup.parent_name)
        return 1
    else:
        DeleteGroup.parent_name = data
        DeleteGroup.all_groups = db.show_groups(DeleteGroup.parent_name)
        reply_markup = Markup(DeleteGroup.all_groups)
        reply_markup.add_back()
        context.bot.edit_message_text(text="Tap on name to go on next level or write name of group "
                                           "if you want to choose it",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 1


def ending_delete_chat_button(update: Update, context: CallbackContext):
    db = DbModel()
    group_name = update.message.text
    if group_name in DeleteGroup.all_groups:
        chats = db.show_chats(group_name)
        if chats:
            context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=DeleteGroup.message_id)
            reply_markup = Markup(chats)
            update.message.reply_text('Choose a chat:',
                                      reply_markup=reply_markup.return_keyboard())
            DeleteGroup.choice = group_name
            DeleteGroup.all_groups = []
            DeleteGroup.parent_name = None
            return 2
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="This group doesn't have any chats")
            return 1
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='There is no group with this name on current level')
        return 1


def ending_delete_chat(update: Update, context: CallbackContext):
    db = DbModel()
    query = update.callback_query
    data = query.data
    choice = data.split('|||')[0]
    if data == 'exit':
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id)
        return 3
    elif choice in ['prev', 'next']:
        page = int(data.split('|||')[1])
        reply_markup = Markup(DeleteGroup.choice, page)
        reply_markup.next() if choice[0] == 'next' else reply_markup.prev()
        context.bot.edit_message_text(text="Choose a chat:",
                                      chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      reply_markup=reply_markup.return_keyboard())
        return 2
    db.delete_chat(data)
    context.bot.edit_message_text(text='Done!',
                                  chat_id=update.effective_chat.id,
                                  message_id=query.message.message_id)
    DeleteGroup.choice = None
    return 3


def add_user(update: Update, context: CallbackContext):
    db = DbModel()
    group_name = update.message.text
    if group_name in DeleteGroup.all_groups:
        chats = db.show_chats(group_name)
        if chats:
            context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=DeleteGroup.message_id)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="Write name of user:")
            DeleteGroup.choice = group_name
            DeleteGroup.all_groups = []
            DeleteGroup.parent_name = None
            return 2
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="This group doesn't have any chats")
            return 1
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='There is no group with this name on current level')
        return 1


def ending_add_user(update: Update, context: CallbackContext):
    username = update.message.text
    db = DbModel
    group_name = DeleteGroup.choice
    chats = db.show_chats(group_name)
    for chat in chats:
        result = add_user(chat, username)
        context.bot.send_message(chat_id=update.effective_chat.id, text=result)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text='Done!')
    DeleteGroup.choice = None
    return 3


@run_async
def show_chats(update: Update, context: CallbackContext):
    db = DbModel()
    group_name = update.message.text
    if group_name in DeleteGroup.all_groups:
        chats = db.show_chats(group_name)
        if chats:
            context.bot.delete_message(chat_id=update.effective_chat.id,
                                       message_id=DeleteGroup.message_id)
            text = "It's a list of chats for group {}:\n".format(group_name)
            for chat_name in chats:
                text += '{}\n'.format(chat_name)
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text=text)
            DeleteGroup.all_groups = []
            DeleteGroup.parent_name = None
            return 2
        else:
            context.bot.send_message(chat_id=update.effective_chat.id,
                                     text="This group doesn't have any chats")
            DeleteGroup.all_groups = []
            DeleteGroup.parent_name = None
            return 2
    else:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='There is no group with this name on current level')
        return 1


@run_async
def error(update: Update, context: CallbackContext):
    text = "I don't know what to do with this: {}".format(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)
