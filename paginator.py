from telebot import types


class Paginator:
    __curr_page_num = 0
    __btn = {
        'next': types.InlineKeyboardButton('>', callback_data='next'),
        'prev': types.InlineKeyboardButton('<', callback_data='previous'),
        'empty': types.InlineKeyboardButton(' ', callback_data='no')}
    __digit_stikers = ['0️⃣', '1️⃣', '2️⃣',
                       '3️⃣', '4️⃣', '5️⃣', '7️⃣', '8️⃣', '9️⃣']
    data_pages_list = []

    def __init__(self, data_list, msg_chat_id,  split=3, final_tip='', start_tip='', msg_max_len = 1000):
        self.split = split
        self.MSG_MAX_LEN = msg_max_len
        self.__divide(data_list)
        self.start_tip = start_tip
        self.chat_id = msg_chat_id
        self.final_tip = final_tip
        self.__generate_btns(split)

    def add_to_data(self, additional_data):
        self.__divide(additional_data)

    def make_first_page(self):
        '''
        this method send first page with buttons of all items and button next, 
        if all content does not fit
        '''
        msg = self.start_tip
        markup = types.InlineKeyboardMarkup(row_width=5)
        pointer = 0
        if len(self.data_pages_list) > 1:
            markup.add(self.__btn['next'])
        btn_row = []
        for item in self.data_pages_list[0]:
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

        # bot.edit_message_text(chat_id=self.chat_id,
        #   message_id=msg_id, text=msg, reply_markup=markup)
        return (msg, markup)

    def make_only(self, num, custom_button_names=[], callback_datas=[]):
        '''
        this method change message text to describtion of one item and change markup to: 
        1) button with text 'back' 
        2) (optional) custom buttons with names from ! list ! custom_button_names 
           and callback_data from ! list ! callback_datas
        '''
        assert isinstance(custom_button_names, list)
        assert isinstance(callback_datas, list)
        assert len(custom_button_names) == len(callback_datas)

        markup = types.InlineKeyboardMarkup()
        msg = 'жужа'
        print(self.data_pages_list[self.__curr_page_num][num-1])
        return (msg, markup)

    def clear_data(self):
        self.data_pages_list = []

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
