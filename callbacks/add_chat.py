from callbacks import run_async, Update, CallbackContext, json, InlineKeyboardButton, InlineKeyboardMarkup, os


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
                            [InlineKeyboardButton('exit', callback_data='exit'.format(page - 1))]] \
                if (len(all_groups) - 5 * page > 5) else \
                [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                  InlineKeyboardButton('exit', callback_data='exit'.format(page - 1))]]
        else:
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page - 1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page + 1))],
                            [InlineKeyboardButton('exit', callback_data='exit'.format(page - 1))]] \
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
    with open('choosing_group_for_adding.txt', 'w') as file:
        file.write(data)
    context.bot.edit_message_text(chat_id=query.message.chat_id,
                                  message_id=query.message.message_id,
                                  text='You choose {}\nWrite a chat name:'.format(data))
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
