from telegram import InlineQueryResultArticle, InputTextMessageContent, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackContext, CallbackQueryHandler
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
        context.bot.send_message(chat_id=update.effective_chat.id, text='You should write a group name without " ". Use "_"')
        return

    with open('groups.json', 'r') as file:
        all_groups: dict = json.loads(file.read())

    if group_name in list(all_groups.keys()):
        context.bot.send_message(chat_id=update.effective_chat.id, text='This group already exist')
        return

    all_groups[group_name] = {'chats': [], 'users': []}
    with open('groups.json', 'w') as file:
        file.write(json.dumps(all_groups))
    context.bot.send_message(chat_id=update.effective_chat.id, text="I've done!")


@run_async
def show_groups(update: Update, context: CallbackContext):
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    text = "It's a list of all groups:\n"
    for name in all_groups.keys():
        text += '{}\n'.format(name)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


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
        return
    if ' ' in chat_name:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text='You should write a chat name without " ". Please use "_"')
        return
    with open('groups.json', 'r') as file:
        all_groups = json.loads(file.read())
    keyboard = list()
    for group_name in list(all_groups.keys()):
        print(group_name)
        keyboard.append([InlineKeyboardButton(group_name, callback_data='|||'.join([group_name, chat_name]))])
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose a group:', reply_markup=reply_markup)


def add_chat_button(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data.split('|||')
    chosen_group, chat_name = data[0], data[1]
    print(chosen_group, chat_name)
    context.bot.send_message(chat_id=update.effective_chat.id, text='ha loh i niche ne delaiu')


@run_async
def error(update: Update, context: CallbackContext):
    text = "I don't know what to do with this: {}".format(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help_callback)
add_group_handler = CommandHandler('add_group', add_group)
show_groups_handler = CommandHandler('show_groups', show_groups)
delete_groups_handler = CommandHandler('delete_group', delete_groups)
add_chat_handler = CommandHandler('add_chat', add_chat)
add_chat_button_handler = CallbackQueryHandler(add_chat_button)
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
    dispatcher.add_handler(add_chat_button_handler)
    dispatcher.add_handler(error_handler)

    updater.start_polling()
    updater.idle()
