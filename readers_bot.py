import telebot
from telebot import types
import config
import msg
from scrapper import Scrapper
# from librarian_bot import send_real_time_req
from paginator import Paginator
from db.db_worker import db_worker
import pickledb

bot = telebot.TeleBot(config.U_BOT_TOKEN)
pgt = ''
scr = ''

statesdb = pickledb.load('readers_states.db', False) 

def create_libraries_markup_from_list(libs):
    mrkp = types.InlineKeyboardMarkup()
    l = []
    for lib in libs:
        while '\n' in lib:
            lib = lib.replace('\n', '')
        while ' ' in lib:
            lib = lib.replace(' ','')
        while '(' in lib:
            lib = lib[:lib.index('(')]
        l.append(lib)

        if lib == 'им.Б.МашукаВзрослоеотделение':
            mrkp.add(types.InlineKeyboardButton('им. Б. Машука (Институтская, 10/1)', callback_data='lib_mashuk'))
        if lib == 'БИЦ':
            pass
            # mrkp.add(types.InlineKeyboardButton('им. Б. Машука (Институтская 10/1)', callback_data='back_to_list'))
        if lib == 'Центральная':
            mrkp.add(types.InlineKeyboardButton('Центральная (Красноармейская, 128)', callback_data='lib_central'))
        if lib == 'Диалог':
            mrkp.add(types.InlineKeyboardButton('Диалог (Политехническая, 46)', callback_data='lib_dialog'))
        if lib == 'Солнечная':
            mrkp.add(types.InlineKeyboardButton('Солнечная (Пограничная, 124/3)', callback_data='lib_sun'))
        if lib == 'Плодопитомник':
            mrkp.add(types.InlineKeyboardButton('Плодопитомник (с. Плодопитомник, ул. Центральная, 1)', callback_data='lib_plodop'))
        if lib == 'Детскаяим.П.Комарова':
            mrkp.add(types.InlineKeyboardButton('им. Комарова (ул. Лазо, 42)', callback_data='lib_komarova'))
        if lib == 'Багульник':
            mrkp.add(types.InlineKeyboardButton('Багульник (п. Моховая Падь, Л-2)', callback_data='lib_baguln'))
        if lib == 'Домсемьи':
            mrkp.add(types.InlineKeyboardButton('Дом Семьи (Пионерская, 157)', callback_data='lib_domsem'))
        if lib == 'Садовое':
            mrkp.add(types.InlineKeyboardButton('Садовое (с. Садовое, ул. Юбилейная,13)', callback_data='lib_sadovoe'))
        if lib == 'Белогорье':
            mrkp.add(types.InlineKeyboardButton('Белогорье (с. Белогорье, ул. Релочная, 22)', callback_data='lib_belogor'))
        if lib == 'ДЮБимА.Чехова':
            mrkp.add(types.InlineKeyboardButton('им. Чехова (Комсомольская 3)', callback_data='lib_chehova'))
        if lib == 'им.Б.МашукаДетскоеотделение':
            mrkp.add(types.InlineKeyboardButton('им. Б. Машука (Институтская, 10/1)', callback_data='lib_mashuk'))
    mrkp.add(types.InlineKeyboardButton('назад к списку', callback_data='back_to_list'))
    return mrkp

#####################################################################
# Create request lib_btn handlers

@bot.callback_query_handler(lambda click: click.data[:4] == 'lib_')
def lib(click):
    lib_name = ''
    if click.data[5:] == 'sadovoe':
        lib_name = 'садовое'
    if click.data[5:] == 'mashuk':
        lib_name = 'машука'
    if click.data[5:] == 'chehova':
        lib_name = 'чехова'
    if click.data[5:] == 'belogor':
        lib_name = 'белогорье'
    if click.data[5:] == 'domsem':
        lib_name = 'дом семьи'
    if click.data[5:] == 'm_pad':
        lib_name = 'моховая'
    if click.data[5:] == 'baguln':
        lib_name = 'багульник'
    if click.data[5:] == 'komarova':
        lib_name = 'комарова'
    if click.data[5:] == 'plodop':
        lib_name = 'плодопитомник'
    if click.data[5:] == 'sun':
        lib_name = 'солнечная'
    if click.data[5:] == 'dialog':
        lib_name = 'диалог'
    if click.data[5:] == 'central':
        lib_name = 'центральная'
    if click.data[5:] == 'mashuk':
        lib_name = 'машука'
    
    global BOOK_NAME
    db = db_worker(config.db_path)
    db.add_request(click.from_user.id, BOOK_NAME, lib_name)
    print(*db.get_all_requests(), sep = '\n\n')
    db.close()

    # send_real_time_req()

    mrkp = types.InlineKeyboardMarkup()
    mrkp.add(types.InlineKeyboardButton('назад к списку',callback_data='back_to_list'))
    bot.edit_message_text('запрос отпрален, чтобы найти другую книгу введите /find_book', 
                            click.from_user.id, click.message.message_id, reply_markup=mrkp)




#####################################################################

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, msg.start_message)

#####################################################################
# BOOK FINDING

@bot.message_handler(commands=['find_book'])
def start_book_find(message):
    bot.send_message(message.chat.id, msg.book_name,
                     parse_mode='markdown')
    statesdb.set(str(message.chat.id), 'ENTER_BOOK_NAME')

# тут где-то фильтры добавить

@bot.message_handler(func=lambda message: statesdb.get(str(message.chat.id)) == "ENTER_BOOK_NAME")
def search_book(message):
    bot.send_message(message.chat.id, msg.please_wait)
    # bot.send_animation(message.chat.id, msg.wait_gif_url)
    global scr
    if not isinstance(scr, str):
        scr.close() 
    scr = Scrapper(config.BookFindServiceUrl_alt)                                    #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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



# FOR PAGINATION
@bot.callback_query_handler(lambda click: click.data == 'next' or click.data == 'previous')
def pagin_btns(click):
    global pgt
    global scr
    if click.data == 'next':
        books = scr.find_next()
        if len(books) != 0:
            add_books = [b.to_str() for b in books]
            pgt.add_to_data(add_books)
        mess, mrkp = pgt.make_next_page()
        bot.edit_message_text(mess, message_id=click.message.message_id,
                              reply_markup=mrkp, chat_id=click.from_user.id)
    elif click.data == 'previous':
        mess, mrkp = pgt.make_previous_page()
        bot.edit_message_text(mess, message_id=click.message.message_id,
                              reply_markup=mrkp, chat_id=click.from_user.id)

libs = None
BOOK_NAME = None
@bot.callback_query_handler(lambda click: click.data[:4] == 'item')
def pagin_one_i(click):    
    global pgt         
    mess, mrkp = pgt.make_one(int(click.data[4])-1, ['назад к списку', 'запросить наличие'], ['back_to_list', 'check_available'])
    bot.edit_message_text(mess, message_id=click.message.message_id,
                            reply_markup=mrkp, chat_id=click.from_user.id)
    global libs
    libs = mess[mess.index('Библиотеки:') + 12:]
    global BOOK_NAME
    BOOK_NAME = mess[:mess.index('Библиотеки:')]

@bot.callback_query_handler(lambda click: click.data == 'check_available')
def check_avail(click): 
    msg = 'Выберите библиотеку:'
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    global libs
    libs = [l for l in libs.split('🔸')]
    markup = create_libraries_markup_from_list(libs)
    bot.edit_message_text(msg, message_id=click.message.message_id,
                            reply_markup=markup, chat_id=click.from_user.id)

@bot.callback_query_handler(func=lambda click: click.data == 'back_to_list')
def back_to_list(click):
    global pgt
    mess, mrkp = pgt.make_first_page()
    bot.edit_message_text(mess, message_id=click.message.message_id,
                          reply_markup=mrkp, chat_id=click.from_user.id)

############################################################################################################
# EVENTS

@bot.message_handler(commands=['events'])
def events(message):
    bot.send_message(message.chat.id, msg.start_message)

############################################################################################################
# RUN

if __name__ == "__main__":
    bot.polling(none_stop=True)



def send_response_to_reader(chat_id, response, req_id):
    '''Вам пришел ответ по поводу вашего запроса:
    книга: 
    библиотека:
    
    текст ответа:'''
    pass

