from callbacks import InlineKeyboardButton, InlineKeyboardMarkup


class Markup:
    def __init__(self, data, page=0, select=0):
        """В случае если пользователь только вызвал команду delete, add итд, после создания экземпляра класса
        надо просто вызвать метод return_keyboard, дефолтные значения уже заложены в классе"""
        self.select = select
        self.data = data
        self.page = page
        self.end_keyboard = [[InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page + 1))],
                             [InlineKeyboardButton('exit', callback_data='exit')]] \
            if len(data) > 5 else [[InlineKeyboardButton('exit', callback_data='exit')]]

    def add_back(self):
        back_button = [InlineKeyboardButton('back', callback_data='back')]
        self.end_keyboard[len(self.end_keyboard)], self.end_keyboard[len(self.end_keyboard) - 1] = \
            self.end_keyboard[len(self.end_keyboard) - 1], back_button

    def current(self):
        if len(self.data) - 5 * self.page > 5 and self.page > 0:
            self.end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(self.page - 1)),
                                  InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page + 1))],
                                 [InlineKeyboardButton('exit', callback_data='exit')]]
        elif self.page == 0:
            self.end_keyboard = [[InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page + 1))],
                                 [InlineKeyboardButton('exit', callback_data='exit')]]
        else:
            self.end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(self.page - 1))],
                                 [InlineKeyboardButton('exit', callback_data='exit')]]

    def add_select(self):
        select_off = [InlineKeyboardButton('select: off', callback_data='select|||1|||{}'.format(self.page))]
        select_on = [InlineKeyboardButton('select: on', callback_data='select|||0|||{}'.format(self.page))]
        if self.select == 0:
            self.end_keyboard[len(self.end_keyboard)], self.end_keyboard[len(self.end_keyboard) - 1] = \
                self.end_keyboard[len(self.end_keyboard) - 1], select_off
        elif self.select == 1:
            self.end_keyboard[len(self.end_keyboard)], self.end_keyboard[len(self.end_keyboard) - 1] = \
                self.end_keyboard[len(self.end_keyboard) - 1], select_on

    def next(self):
        """Метод, который вызывается, в случае если пользователь нажал на next.
        меняет финальные кнопки"""
        self.end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(self.page - 1)),
                              InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page + 1))],
                             [InlineKeyboardButton('exit', callback_data='exit')]] \
            if (len(self.data) - 5 * self.page > 5) else \
            [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(self.page - 1))],
             [InlineKeyboardButton('exit', callback_data='exit')]]

    def prev(self):
        """Метод, который вызывается, в случае если пользователь нажал на prev.
        меняет финальные кнопки"""
        self.end_keyboard = [[InlineKeyboardButton('prev', callback_data='prev|||{}'.format(self.page - 1)),
                              InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page + 1))],
                             [InlineKeyboardButton('exit', callback_data='exit')]] \
            if (self.page > 0) else \
            [[InlineKeyboardButton('next', callback_data='next|||{}'.format(self.page + 1))],
             [InlineKeyboardButton('exit', callback_data='exit')]]

    def return_keyboard(self):
        """Метод, который используется для возврата готовой разметки кнопок"""
        keyboard = list()
        for group_name in list(self.data.keys())[5 * self.page:5 * (self.page + 1)] \
                if isinstance(self.data, dict) else self.data[5 * self.page:5 * (self.page + 1)]:
            keyboard.append([InlineKeyboardButton(group_name, callback_data=group_name+'|||{}'.format(self.select))])
        keyboard.extend(self.end_keyboard)
        return InlineKeyboardMarkup(keyboard)
