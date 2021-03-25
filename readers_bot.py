import telebot
from telebot import types
import config
import msg
from scrapper import Scrapper
from paginator import Paginator
from db.db_worker import db_worker
import pickledb
from loguru import logger 

logger.add("logs/reader_debug.log", format="{time:YYYY-MM-DD at HH:mm:ss} {level} {message}", level="DEBUG", rotation="100 MB", compression="zip", backtrace=True, diagnose=True)


bot = telebot.TeleBot(config.U_BOT_TOKEN)
pgt = ''
scr = ''

statesdb = pickledb.load('readers_states.db', False)


##############################################################################
# utility func

def create_libraries_markup_from_list(libs):
    mrkp = types.InlineKeyboardMarkup()
    l = []
    for lib in libs:
        while '\n' in lib:
            lib = lib.replace('\n', '')
        while ' ' in lib:
            lib = lib.replace(' ', '')
        while '(' in lib:
            lib = lib[:lib.index('(')]
        l.append(lib)

        if lib == 'им.Б.МашукаВзрослоеотделение':
            mrkp.add(types.InlineKeyboardButton(
                'им. Б. Машука (Институтская, 10/1)', callback_data='lib_mashuk'))
        if lib == 'БИЦ':
            pass
            # mrkp.add(types.InlineKeyboardButton('им. Б. Машука (Институтская 10/1)', callback_data='back_to_list'))
        if lib == 'Центральная':
            mrkp.add(types.InlineKeyboardButton(
                'Центральная (Красноармейская, 128)', callback_data='lib_central'))
        if lib == 'Диалог':
            mrkp.add(types.InlineKeyboardButton(
                'Диалог (Политехническая, 46)', callback_data='lib_dialog'))
        if lib == 'Солнечная':
            mrkp.add(types.InlineKeyboardButton(
                'Солнечная (Пограничная, 124/3)', callback_data='lib_sun'))
        if lib == 'Плодопитомник':
            mrkp.add(types.InlineKeyboardButton(
                'Плодопитомник (с. Плодопитомник, ул. Центральная, 1)', callback_data='lib_plodop'))
        if lib == 'Детскаяим.П.Комарова':
            mrkp.add(types.InlineKeyboardButton(
                'им. Комарова (ул. Лазо, 42)', callback_data='lib_komarova'))
        if lib == 'Багульник':
            mrkp.add(types.InlineKeyboardButton(
                'Багульник (п. Моховая Падь, Л-2)', callback_data='lib_baguln'))
        if lib == 'Домсемьи':
            mrkp.add(types.InlineKeyboardButton(
                'Дом Семьи (Пионерская, 157)', callback_data='lib_domsem'))
        if lib == 'Садовое':
            mrkp.add(types.InlineKeyboardButton(
                'Садовое (с. Садовое, ул. Юбилейная,13)', callback_data='lib_sadovoe'))
        if lib == 'Белогорье':
            mrkp.add(types.InlineKeyboardButton(
                'Белогорье (с. Белогорье, ул. Релочная, 22)', callback_data='lib_belogor'))
        if lib == 'ДЮБимА.Чехова':
            mrkp.add(types.InlineKeyboardButton(
                'им. Чехова (Комсомольская 3)', callback_data='lib_chehova'))
        if lib == 'им.Б.МашукаДетскоеотделение':
            mrkp.add(types.InlineKeyboardButton(
                'им. Б. Машука (Институтская, 10/1)', callback_data='lib_mashuk'))
    mrkp.add(types.InlineKeyboardButton(
        'назад к списку', callback_data='back_to_list'))
    return mrkp

##############################################################################
# SENDING MESSGAES FROM LIBRARIANS BOT

# SEND REALTIME REQUEST
def send_req(chat_id, resp_text, req_id=None):
    lib_bot = telebot.TeleBot(config.E_BOT_TOKEN)
    msg = 'Вам пришел запрос: \nкнига: ' + resp_text
    if req_id:
        msg += '\nномер запроса:{}'.format(req_id)
    mrkp = telebot.types.InlineKeyboardMarkup()
    mrkp.add(telebot.types.InlineKeyboardButton('ответить', 
                                                callback_data='response'))
    lib_bot.send_message(chat_id, msg, reply_markup=mrkp)

# SEND RESERVATION NOTIF
def send_reservation_mess_to_lib(req_id, name):
    db = db_worker(config.db_path)
    request_data = db.get_request_by_id(req_id)
    book = request_data[2]
    libname = book[3]
    librarians_id = db.get_all_unmute_librarians_id_from_one_lib(libname)
    # добавить в отложенные
    db.close()

    mess = 'Пользователь {} зарезервировал книгу\n'.format(name) + book + \
           'Пожалуйста, отложите книгу на два дня.'

    lib_bot = telebot.TeleBot(config.E_BOT_TOKEN)
    for _id in librarians_id:
        lib_bot.send_message(_id, mess) 

# SEND REQUEST TO LIBRARIANS
@bot.callback_query_handler(lambda click: click.data[:4] == 'lib_')
def lib(click):
    lib_name = ''
    if click.data[4:] == 'sadovoe':
        lib_name = 'cадовое'
    if click.data[4:] == 'mashuk':
        lib_name = 'машука'
    if click.data[4:] == 'chehova':
        lib_name = 'чехова'
    if click.data[4:] == 'belogor':
        lib_name = 'белогорье'
    if click.data[4:] == 'domsem':
        lib_name = 'дом семьи'
    if click.data[4:] == 'm_pad':
        lib_name = 'моховая'
    if click.data[4:] == 'baguln':
        lib_name = 'багульник'
    if click.data[4:] == 'komarova':
        lib_name = 'комарова'
    if click.data[4:] == 'plodop':
        lib_name = 'плодопитомник'
    if click.data[4:] == 'sun':
        lib_name = 'солнечная'
    if click.data[4:] == 'dialog':
        lib_name = 'диалог'
    if click.data[4:] == 'central':
        lib_name = 'центральная'
    if click.data[4:] == 'mashuk':
        lib_name = 'машука'

    global BOOK_NAME
    db = db_worker(config.db_path)
    req_id = db.add_request(click.from_user.id, BOOK_NAME, lib_name)
    libraians_id = db.get_all_unmute_librarians_id_from_one_lib(lib_name)
    db.close()

    for id_ in libraians_id:
        send_req(id_, BOOK_NAME, req_id)
    mrkp = types.InlineKeyboardMarkup()
    mrkp.add(types.InlineKeyboardButton('назад к списку', 
                                        callback_data='back_to_list'))
    bot.edit_message_text(msg.req_send_reader_tip, click.from_user.id, 
                          click.message.message_id, reply_markup=mrkp)
    logger.debug("{id} : send request n {id1} to {lib} librarian", id = click.from_user.id, id1 = req_id, lib = click.data[4:])


##############################################################################
# START
@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, msg.start_message)
    logger.debug("{id} : welcome message", id = message.chat.id)


##############################################################################
# BOOK FINDING

# /FIND_BOOK
@bot.message_handler(commands=['find_book'])
def start_book_find(message):
    bot.send_message(message.chat.id, msg.book_name,
                     parse_mode='markdown')
    statesdb.set(str(message.chat.id), 'ENTER_BOOK_NAME')
    logger.debug("{id} : start book finding", id = message.chat.id)

# тут где-то фильтры добавить

# SEND BOOKS LIST
@bot.message_handler(func=lambda message: statesdb.get(str(message.chat.id)) == "ENTER_BOOK_NAME" 
                    and statesdb.get(str(message.message_id)) != "READER_NAME_WAITE" and 
                    message.text not in ['/reserved_books', '/events', '/find_book'])
def search_book(message):
    bot.send_message(message.chat.id, msg.please_wait)
    global scr
    if not isinstance(scr, str):
        scr.close()
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    scr = Scrapper(config.BookFindServiceUrl, message.chat.id, message.message_id)
    books = scr.find_books(message.text)
    if books:
        books = [b.to_str() for b in books]
        global pgt
        if not isinstance(pgt, str):
            pgt.clear_data()
        pgt = Paginator(books, final_tip=msg.books_list_req_tip, split=3)
        mess, mrkp = pgt.make_first_page()
        bot.send_message(message.chat.id, mess, reply_markup=mrkp)
        statesdb.set(str(message.chat.id), 'PAGINATOR_ACTIVE')
    else:
        bot.send_message(message.chat.id, msg.not_found)

    logger.debug("{id} : get first pagination page", id = message.chat.id)


# LEAFING BOOKS LIST
@bot.callback_query_handler(lambda click: click.data == 'next' or 
                                          click.data == 'previous')
def pagin_btns(click):
    global pgt
    global scr
    if click.data == 'next':
        books = scr.find_next()
        if len(books) != 0:
            add_books = [b.to_str() for b in books]
            pgt.add_to_data(add_books)
        mess, mrkp = pgt.make_next_page()
        bot.edit_message_text(text=mess, 
                              message_id=click.message.message_id,
                              reply_markup=mrkp, 
                              chat_id=click.from_user.id)
        logger.debug("{id} : get next pagination page", id = click.from_user.id)
    elif click.data == 'previous':
        mess, mrkp = pgt.make_previous_page()
        bot.edit_message_text(mess, message_id=click.message.message_id,
                              reply_markup=mrkp, chat_id=click.from_user.id)
        logger.debug("{id} : get previous pagination page", id = click.from_user.id)


##############################################################################
# FORMATE RESERVATION QUERY

@bot.callback_query_handler(lambda click: click.data == 'reserve')
def reserve(click):
    mess = click.message.text
    bot.edit_message_text(mess + '\n❗️Введите ваше имя❗️',
                          click.from_user.id, click.message.message_id)
    statesdb.set(str(click.from_user.id), "READER_NAME_WAITE")
    logger.debug("{id} : click reserve button, system wait name", id = click.from_user.id)


@bot.message_handler(func=lambda message: statesdb.get(str(message.chat.id)) 
                                                      == "READER_NAME_WAITE")
def get_user_name(message):
    reader_name = message.text
    db = db_worker(config.db_path)
    # db.add_response()
    # поменять ответ в бд на книга отложена
    # send_reservation_mess_to_lib(req_id)
    bot.send_message(message.chat.id, msg.get_book_instructions_to_reader)
    statesdb.set(str(message.chat.id), 'END')
    logger.debug("{id} : get user name for request", id = message.chat.id)


@bot.message_handler(commands=['reserved_books'])
def show_reserved_books(message):
    db = db_worker(config.db_path)
    books = db.get_reserved_books_for_reader(message.chat.id)
    db.close()
    print(books)

    statesdb.set(str(message.chat.id), 'END')
    logger.debug("{id} : get reserved books list", id = message.chat.id)


##############################################################################
# ONE BOOK WORK
libs = ''
BOOK_NAME = None


# ONE BOOK MSG
@bot.callback_query_handler(lambda click: click.data[:4] == 'item')
def pagin_one_i(click):
    global pgt
    mess, mrkp = pgt.make_one(int(click.data[4])-1, 
                              ['назад к списку', 'запросить наличие'], 
                              ['back_to_list', 'check_available'])
    bot.edit_message_text(text=mess, 
                          message_id=click.message.message_id,
                          reply_markup=mrkp, 
                          chat_id=click.from_user.id)
    global libs
    libs = mess[mess.index('В наличии в:') + 12:]
    global BOOK_NAME
    BOOK_NAME = mess[:mess.index('В наличии в:')]
    logger.debug("{id} : get next pagination page", id = click.from_user.id)


# BACK TO BOOKS LIST FROM ONE BOOK MSG
@bot.callback_query_handler(func=lambda click: click.data == 'back_to_list')
def back_to_list(click):
    global pgt
    mess, mrkp = pgt.make_first_page()
    bot.edit_message_text(mess, message_id=click.message.message_id,
                          reply_markup=mrkp, chat_id=click.from_user.id)
    logger.debug("{id} : update books list", id = click.from_user.id)


# CHANGE MARKUP TO LIBRARIES BUTTONS
@bot.callback_query_handler(lambda click: click.data == 'check_available')
def check_avail(click):
    msg = 'Выберите библиотеку:'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    global libs
    libs = [l for l in libs.split('🔸')]
    markup = create_libraries_markup_from_list(libs)
    bot.edit_message_text(msg, message_id=click.message.message_id,
                          reply_markup=markup, chat_id=click.from_user.id)
    logger.debug("{id} : change markup to libraries buttons", id = click.from_user.id)


##############################################################################


# EVENTS
@bot.message_handler(commands=['events'])
def events(message):
    bot.send_message(message.chat.id, msg.start_message)


##############################################################################


@bot.message_handler(content_types='text')
def other_inp(message):
    mess = 'я вас не понимаю, давайте попробуем ещё раз\n' + msg.start_message
    bot.send_message(message.chat.id, mess)
    logger.debug("{id} : other input", id = message.chat.id)

# RUN
if __name__ == "__main__":
    bot.polling(none_stop=True)
