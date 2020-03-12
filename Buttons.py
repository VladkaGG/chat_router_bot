from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Markup:
    def __init__(self, data, page=0):
        """В случае если пользователь только вызвал команду delete, add итд, после создания экземпляра класса
        надо просто вызвать метод return_keyboard, дефолтные значения уже заложены в классе"""
        self.data = data
        self.page = page
        self.end_keyboard = [InlineKeyboardButton('exit', callback_data='exit'),
                             InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page+1))]

    def next(self):
        """Метод, который вызывается, в случае если пользователь нажал на next.
        меняет финальные кнопки"""
        self.end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(self.page - 1)),
                              InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page + 1))],
                             [InlineKeyboardButton('exit', callback_data='exit')]] \
            if (len(self.data) - 5 * self.page > 5) else \
            [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(self.page - 1)),
              InlineKeyboardButton('exit', callback_data='exit')]]

    def prev(self):
        """Метод, который вызывается, в случае если пользователь нажал на prev.
        меняет финальные кнопки"""
        self.end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(self.page - 1)),
                              InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page + 1))],
                             [InlineKeyboardButton('exit', callback_data='exit')]] \
            if (self.page > 0) else \
            [[InlineKeyboardButton('exit', callback_data='exit'),
              InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page + 1))]]

    def return_keyboard(self):
        """Метод, который используется для возврата готовой разметки кнопок"""
        keyboard = list()
        for group_name in list(self.data.keys())[5 * self.page:5 * (self.page + 1)]:
            keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name)])
        keyboard.extend(self.end_keyboard)
        return InlineKeyboardMarkup(keyboard)
