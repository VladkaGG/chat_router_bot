from callbacks import run_async, Update, CallbackContext, json, InlineKeyboardButton, InlineKeyboardMarkup, os


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
                [InlineKeyboardButton('exit', callback_data='exit'.format(page - 1))]] \
                if (len(all_chats) - 5 * page > 5) else \
                [[InlineKeyboardButton('prev', callback_data='prev|||{}|||{}'.format(page - 1, chosen_group)),
                  InlineKeyboardButton('exit', callback_data='exit'.format(page - 1))]]
        else:
            end_keyboard = [
                [InlineKeyboardButton('prev', callback_data='prev|||{}|||{}'.format(page - 1, chosen_group)),
                 InlineKeyboardButton('next', callback_data='next|||{}|||{}'.format(page + 1, chosen_group))],
                [InlineKeyboardButton('exit', callback_data='exit'.format(page - 1))]] \
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
