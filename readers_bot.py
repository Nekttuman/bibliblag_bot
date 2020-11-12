import telebot
from telebot import types
import config
import msg
from scrapper import Scrapper
# import employee_bot


bot = telebot.TeleBot(config.U_BOT_TOKEN)
pgt = ''
scr = ''


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, msg.start_message)

# BOOK FINDING
BookFindingOn = False
@bot.message_handler(commands=['find_book'])
def start_book_find(message):
    bot.send_message(message.chat.id, msg.name_author_format,
                     parse_mode='markdown')
    global BookFindingOn
    BookFindingOn = True
    global scr
    if not isinstance(scr, str):
        scr.close_browser()
    global pgt
    if not isinstance(pgt, str):
        pgt.clear_data()


class Paginator:
    __curr_page_num = 0
    __btn = {
        'next': types.InlineKeyboardButton('>', callback_data='next'),
        'prev': types.InlineKeyboardButton('<', callback_data='previous'),
        'empty': types.InlineKeyboardButton(' ', callback_data='no')}
    __digit_stikers = ['0️⃣', '1️⃣', '2️⃣',
                       '3️⃣', '4️⃣', '5️⃣', '7️⃣', '8️⃣', '9️⃣']
    data_pages_list = []
    def __init__(self, data_list, msg_chat_id,  split=3, final_tip='', start_tip=''):
        self.split = split
        self.__divide(data_list)
        self.start_tip = start_tip
        self.chat_id = msg_chat_id
        self.final_tip = final_tip
        self.__generate_btns(split)

    def add_to_data(self, additional_data):
        self.__divide(additional_data)

    def send_first_page(self):
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
        bot.send_message(self.chat_id, msg, reply_markup=markup)

    def send_next_page(self, msg_id):
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

        bot.edit_message_text(chat_id=self.chat_id,
                              message_id=msg_id, text=msg, reply_markup=markup)

    def send_previous_page(self, msg_id):
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

        bot.edit_message_text(chat_id=self.chat_id,
                              message_id=msg_id, text=msg, reply_markup=markup)

    def send_only(self, msg_id, num, custom_button_names=[], callback_datas=[]):
        '''
        this method change message text to describtion of one item and change markup to: 
        1) button with text 'back' 
        2) (optional) custom buttons with names from ! list ! custom_button_names 
           and callback_data from ! list ! callback_datas
        '''
        assert isinstance(custom_button_names, list)
        assert isinstance(callback_datas, list)
        assert len(custom_button_names) == len(callback_datas)

    def clear_data(self):
        self.data_pages_list = []

    def __overlen(self, lst, item):
        size = 0
        for i in lst:
            size += len(i)
        size += len(item)
        return size > 700

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


@bot.message_handler(content_types=['text'])
def search_book(message):
    global BookFindingOn
    if BookFindingOn:
        bot.send_message(message.chat.id, msg.please_wait)
        bot.send_animation(message.chat.id, msg.wait_gif_url)
        global scr
        scr = Scrapper(config.BookFindServiceUrl_alt)
        books = scr.find_books(message.text)

        if books:
            books = [b.to_str() for b in books]

            global pgt
            pgt = Paginator(books, final_tip=msg.books_list_req_tip, msg_chat_id=message.chat.id, split=3)
            pgt.send_first_page()
            BookFindingOn = False
        else:
            bot.send_message(message.chat.id, msg.not_found)
            scr.close_browser()
    else:
        bot.send_message(message.chat.id, 'Давай попробуем ещё раз')
        welcome(message)


# FOR PAGINATION
@bot.callback_query_handler(lambda click: click.data == 'next' or click.data == 'previous' or click.data[:4] == 'book')
def pagin_btns(click):
    global pgt
    global scr
    if click.data == 'next':
        books = scr.find_next()
        if len(books) != 0:
            add_books = [b.to_str() for b in books]
            pgt.add_to_data(add_books)
        else:
            scr.close_browser()
        pgt.send_next_page(click.message.message_id)
    elif click.data == 'previous':
        pgt.send_previous_page(click.message.message_id)
    else:
        pgt.send_only(click.message.message_id, int(click.data[4]))


# @bot.message_handler(commands=["geo"])
# def geo(message):
#     keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
#     button_geo = types.KeyboardButton(text="Отправить местоположение", request_location=True)
#     keyboard.add(button_geo)
#     bot.send_message(message.chat.id, "Привет! Нажми на кнопку и передай мне свое местоположение", reply_markup=keyboard)

# @bot.message_handler(content_types=["location"])
# def location(message):
#     if message.location is not None:
#         print(message.location)
#         print("latitude: %s; longitude: %s" % (message.location.latitude, message.location.longitude))

@bot.message_handler(commands=['events'])
def events(message):
    bot.send_message(message.chat.id, msg.start_message)


# RUN
if __name__ == "__main__":
    bot.polling(none_stop=True)

    #993803709