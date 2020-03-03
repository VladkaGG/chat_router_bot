from callbacks import run_async, Update, CallbackContext


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
