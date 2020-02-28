from telegram import InlineQueryResultArticle, InputTextMessageContent, Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, InlineQueryHandler, CallbackContext
import json

# import logging

# logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname) - %(message)s', level=logging.INFO)


updater = Updater(token='829440405:AAFzQJ13Kc3d04TeG4dTyd672M4diFsiR7c', use_context=True)
dispatcher = updater.dispatcher
job = updater.job_queue


def start(update: Update, context: CallbackContext):
    user = update.effective_user
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Hello from bot, {}! Type '/help' to get information about me".format(user.username))


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

    text = """It is actual list of my possibilities:\n"""
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


def error(update: Update, context: CallbackContext):
    text = "I don't know what to do with this: {}".format(update.message.text)
    context.bot.send_message(chat_id=update.effective_chat.id, text=text)


# def caps(update: Update, context: CallbackContext):
#     text_caps = ' '.join(context.args).upper()
#     context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)
#
#
# def inline_caps(update: Update, context: CallbackContext):
#     query = update.inline_query.query
#     if not query:
#         return
#     results = list()
#     results.append(
#         InlineQueryResultArticle(
#             id=update.inline_query.id,
#             title='Caps',
#             input_message_content=InputTextMessageContent(query.upper())))
#     context.bot.answer_inline_query(update.inline_query.id, results)
#
#
# def timer(context: CallbackContext):
#     context.bot.send_message(chat_id=context.job.context, text='ALARM MATHAFACKA!!!@!!1')
#
#
# def message_timer(update: Update, context: CallbackContext):
#     context.bot.send_message(chat_id=update.message.chat_id, text='____Setting a timer for 1 minute____')
#     context.job_queue.run_once(timer, 60, context=update.message.chat_id)


start_handler = CommandHandler('start', start)
help_handler = CommandHandler('help', help_callback)
add_group_handler = CommandHandler('add_group', add_group)
show_groups_handler = CommandHandler('show_groups', show_groups)
delete_groups_handler = CommandHandler('delete_group', delete_groups)
# caps_handler = CommandHandler('caps', caps)
# timer_handler = CommandHandler('timer', message_timer)
# inline_caps_handler = InlineQueryHandler(inline_caps)
error_handler = MessageHandler(Filters.text, error)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(help_handler)
dispatcher.add_handler(add_group_handler)
dispatcher.add_handler(show_groups_handler)
dispatcher.add_handler(delete_groups_handler)
# dispatcher.add_handler(caps_handler)
# dispatcher.add_handler(timer_handler)
# dispatcher.add_handler(inline_caps_handler)
dispatcher.add_handler(error_handler)

updater.start_polling()
