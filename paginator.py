from telebot import types


class Paginator:
    '''Из списка с данными делает нарезку на страницы и кнопки к ним'''
    __curr_page_num = 0
    __btn = {
        'next': types.InlineKeyboardButton('далее', callback_data='next'),
        'prev': types.InlineKeyboardButton('назад', callback_data='previous'),
        'empty': types.InlineKeyboardButton(' ', callback_data='no')}
    __digit_stikers = ['0️⃣', '1️⃣', '2️⃣',
                       '3️⃣', '4️⃣', '5️⃣', '7️⃣', '8️⃣', '9️⃣']
    data_pages_list = []

    def __init__(self, data_list, split=3, final_tip='', start_tip='', msg_max_len = 1000):
        self.split = split
        self.MSG_MAX_LEN = msg_max_len
        self.data_pages_list = []
        self.__divide(data_list)
        self.start_tip = start_tip
        self.final_tip = final_tip
        self.__generate_btns(split)

    def add_to_data(self, additional_data):
        self.__divide(additional_data)

    def make_first_page(self):
        '''
        this method send first page with buttons of all items and button next, 
        if all content does not fit
        '''
        self.__curr_page_num = 0
        msg = self.start_tip
        markup = types.InlineKeyboardMarkup(row_width=5)
        pointer = 0
        if len(self.data_pages_list) > 1:
            markup.add(self.__btn['next'])
        btn_row = []
        for item in self.data_pages_list[self.__curr_page_num]:
            msg += self.__digit_stikers[pointer+1] + ' ' + item + '\n'
            btn_row.append(self.__btn[pointer+1])
            pointer += 1
        markup.add(*btn_row)
        msg += '\n' + self.final_tip
        return (msg, markup)

    def make_next_page(self):
        self.__curr_page_num += 1

        markup = types.InlineKeyboardMarkup(row_width=5)
        if self.__curr_page_num + 1 == len(self.data_pages_list):
            markup.add(self.__btn['prev'])
        else:
            markup.add(self.__btn['prev'], self.__btn['next'])

        msg = ''
        btn_row = []
        pointer = 0
        for item in self.data_pages_list[self.__curr_page_num]:
            msg += self.__digit_stikers[pointer+1] + ' ' + item + '\n'
            btn_row.append(self.__btn[pointer+1])
            pointer += 1
        markup.add(*btn_row)
        msg += '\n' + self.final_tip

        return (msg, markup)

    def make_previous_page(self):
        self.__curr_page_num -= 1

        markup = types.InlineKeyboardMarkup(row_width=5)
        if self.__curr_page_num == 0:
            markup.add(self.__btn['next'])
        else:
            markup.add(self.__btn['prev'], self.__btn['next'])

        msg = ''
        btn_row = []
        pointer = 0
        for item in self.data_pages_list[self.__curr_page_num]:
            msg += self.__digit_stikers[pointer+1] + ' ' + item + '\n'
            btn_row.append(self.__btn[pointer+1])
            pointer += 1
        markup.add(*btn_row)
        msg += '\n' + self.final_tip

        return (msg, markup)

    def make_one(self, num, custom_button_names=[], callbacks_data=[]):
        '''
        this method change message text to describtion of one item and change markup to: 
        1) button with text 'back' 
        2) (optional) custom buttons with names from ! list ! custom_button_names 
           and callback_data from ! list ! callback_datas
        '''
        assert isinstance(custom_button_names, list)
        assert isinstance(callbacks_data, list)
        assert len(custom_button_names) == len(callbacks_data)

    
        markup = types.InlineKeyboardMarkup()
        for i in range(len(custom_button_names)):
            markup.add(types.InlineKeyboardButton(custom_button_names[i], callback_data=callbacks_data[i]))

        msg = self.data_pages_list[self.__curr_page_num][num]

        return (msg, markup)

    def get_item(self, num):
        assert isinstance(num, int)
        return self.data_pages_list[self.__curr_page_num][num]

    def clear_data(self):
        self.data_pages_list = []
        self.__curr_page_num = 0

    def __overlen(self, lst, item):
        '''
        проверяет длину сообщения относительно MSG_MAX_LEN
        '''
        size = 0
        for i in lst:
            size += len(i)
        size += len(item)
        return size > self.MSG_MAX_LEN
                     
    def __divide(self, data):
        p = 0
        page = []
        for item in data:
            if len(page) == self.split or self.__overlen(page, item):
                p = 0
                self.data_pages_list.append(page)
                page = []
                page.append(item)
            else:
                p += 1
                page.append(item)

        if len(data) / self.split != 0:
            self.data_pages_list.append(page)

    def __generate_btns(self, num):
        assert num > 0 and num < 10
        for n in range(1, num+1):
            self.__btn[n] = types.InlineKeyboardButton(
                self.__digit_stikers[n], callback_data='item' + str(n))
