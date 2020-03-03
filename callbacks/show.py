from callbacks import run_async, Update, CallbackContext, json, InlineKeyboardButton, InlineKeyboardMarkup


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
                            [InlineKeyboardButton('exit', callback_data='exit'.format(page-1))]] \
                if (len(all_groups) - 5*page > 5) else \
                [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page-1)),
                  InlineKeyboardButton('exit', callback_data='exit'.format(page-1))]]
        else:
            end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(page-1)),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(page+1))],
                            [InlineKeyboardButton('exit', callback_data='exit'.format(page-1))]] \
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
