from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler, \
    ConversationHandler
from telegram.ext.dispatcher import run_async
import json


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
                        '/delete_user': 'Delete user from some group, tell me group',
                        '/update_group': 'Update name of some group',
                        '/show_groups': 'Show all groups'}

    text = """It is actual list of possibilities:\n"""
    for name, description in actual_functions.items():
        text += "{} - {}\n".format(name, description)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


def add_group(update: Update, context: CallbackContext):
    group_name = ' '.join(context.args)
    if not group_name:
        context.bot.send_message(chat_id=update.effective_chat.id, text='You should write a group name after command')
        return
    if ' ' in group_name:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You should write a group name without " ". Use "_"')
        return
    with open('groups.json', 'r') as file:
        all_groups: dict = json.loads(file.read())
    if group_name in list(all_groups.keys()):
        context.bot.send_message(chat_id=update.effective_chat.id, text='This group already exist')
        return
    all_groups[group_name] = {'groups': {}, 'chats': []}
    with open('groups.json', 'w') as file:
        file.write(json.dumps(all_groups))
    context.bot.send_message(chat_id=update.effective_chat.id, text="Done!")


def delete_groups(update: Update, context: CallbackContext):
    group_name = ' '.join(context.args)
    if not group_name:
        context.bot.send_message(chat_id=update.effective_chat.id, text='You should write a group name after command')
        return
    if ' ' in group_name:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You should write a group name without " ". Use "_"')
        return
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    if group_name not in all_groups.keys():
        context.bot.send_message(chat_id=update.effective_chat.id, text="Group {} doesn't exist")
        return
    all_groups.pop(group_name)
    with open('groups.json', 'w') as file:
        file.write(json.dumps(all_groups))
    context.bot.send_message(chat_id=update.effective_chat.id, text="I've done!")


@run_async
def add_chat(update: Update, context: CallbackContext):
    chat_name = ' '.join(context.args)
    if not chat_name:
        context.bot.send_message(chat_id=update.effective_chat.id, text='You should write a chat name after command')
        return 0
    if ' ' in chat_name:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You should write a chat name without " ". Please use "_"')
        return 0
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    keyboard = list()
    for group_name in list(all_groups.keys()):
        keyboard.append([InlineKeyboardButton(group_name, callback_data='|||'.join([group_name, chat_name]))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose a group:', reply_markup=reply_markup)
    return 0


def add_chat_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data.split('|||')
    chosen_group, chat_name = data[0], data[1]
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    if chat_name in all_groups[chosen_group]['chats']:
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text='This chat already exist in this group')
        return 0
    all_groups[chosen_group]['chats'].append(chat_name)
    with open('groups.json', 'w') as file:
        file.write(json.dumps(all_groups))
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text='Done!')
    return 0


@run_async
def delete_chat(update: Update, context: CallbackContext):
    chat_name = ' '.join(context.args)
    if not chat_name:
        context.bot.send_message(chat_id=update.effective_chat.id, text='You should write a chat name after command')
        return
    if ' ' in chat_name:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You should write a chat name without " ". Please use "_"')
        return
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    keyboard = list()
    for group_name in list(all_groups.keys()):
        keyboard.append([InlineKeyboardButton(group_name, callback_data='|||'.join([group_name, chat_name]))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose a group:', reply_markup=reply_markup)


def delete_chat_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data.split('|||')
    chosen_group, chat_name = data[0], data[1]
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    if chat_name not in all_groups[chosen_group]['chats']:
        context.bot.edit_message_text(chat_id=query.message.chat_id,
                                      message_id=query.message.message_id,
                                      text="This chat doesn't exist in this group")
        return 0
    all_groups[chosen_group]['chats'].remove(chat_name)
    with open('groups.json', 'w') as file:
        file.write(json.dumps(all_groups))
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text="Done!")
    return 0


@run_async
def show_groups(update: Update, context: CallbackContext):
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    keyboard = list()
    for group_name in list(all_groups.keys()):
        keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
    keyboard.append([InlineKeyboardButton('exit', callback_data='exit')])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("It's a list of all groups.\nType on group to see list of chats in chosen group",
                              reply_markup=reply_markup)
    return 0


@run_async
def show_chats(update: Update, context: CallbackContext):
    query = update.callback_query
    chosen_group = query.data
    if chosen_group == 'exit':
        context.bot.delete_message(chat_id=query.message.chat_id,
                                   message_id=query.message.message_id,
                                   timeout=0.5)
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='OK')
        return 0
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    if not all_groups[chosen_group]['chats']:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Group {} doesn't have any chats".format(chosen_group))
        return 0
    text = "It's a list of chats for group {}:\n".format(chosen_group)
    for chat_name in all_groups[chosen_group]['chats']:
        text += '{}\n'.format(chat_name)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=text)
    return 0


@run_async
def error(update: Update, context: CallbackContext):
    text = "I don't know what to do with this: {}".format(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help_callback)
add_group_handler = CommandHandler('add_group', add_group)
show_groups_handler = ConversationHandler(entry_points=[CommandHandler('show_groups', show_groups)],
                                          states={
                                              0: [CallbackQueryHandler(show_chats)]
                                          },
                                          fallbacks=[CommandHandler('show_groups', show_groups)])
delete_groups_handler = CommandHandler('delete_group', delete_groups)
add_chat_handler = ConversationHandler(entry_points=[CommandHandler('add_chat', add_chat)],
                                       states={
                                           0: [CallbackQueryHandler(add_chat_button)]
                                       },
                                       fallbacks=[CommandHandler('add_chat', add_chat)])
delete_chat_handler = ConversationHandler(entry_points=[CommandHandler('delete_chat', delete_chat)],
                                          states={
                                              0: [CallbackQueryHandler(delete_chat_button)]
                                          },
                                          fallbacks=[CommandHandler('delete_chat', delete_chat)])
error_handler = MessageHandler(Filters.text, error)

if __name__ == '__main__':
    updater = Updater(token='829440405:AAFzQJ13Kc3d04TeG4dTyd672M4diFsiR7c', use_context=True, workers=20)
    dispatcher = updater.dispatcher
    job = updater.job_queue

    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(add_group_handler)
    dispatcher.add_handler(show_groups_handler)
    dispatcher.add_handler(delete_groups_handler)
    dispatcher.add_handler(add_chat_handler)
    dispatcher.add_handler(delete_chat_handler)
    dispatcher.add_handler(error_handler)

    updater.start_polling()
    updater.idle()
