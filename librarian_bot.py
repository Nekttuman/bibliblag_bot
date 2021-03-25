import telebot
from telebot import types
import config
import msg
from db.lib_tokens import lib_tokens
from db.db_worker import db_worker
from paginator import Paginator
import pickledb
from loguru import logger 

logger.add("logs/librarian_debug.log", format="{time:YYYY-MM-DD at HH:mm:ss} {level} {message}", level="DEBUG", rotation="100 MB", compression="zip", backtrace=True, diagnose=True)



bot = telebot.TeleBot(config.E_BOT_TOKEN)

REQUESTS_LIST_SPLIT = 4


def check_registration(chat_id):
    db = db_worker(config.db_path)
    answer = db.check_librarian(chat_id)
    db.close()
    return answer


def send_response_to_reader(response, req_id, reserve=False):
    db = db_worker(config.db_path)
    req = db.get_request_by_id(req_id)
    db.close()
    msg = '''Вам пришел ответ по поводу вашего запроса: 
    книга: ''' + req[2] + '''
    библиотека: ''' + req[3] + '''

    текст ответа: ''' + response

    red_bot = telebot.TeleBot(config.U_BOT_TOKEN)
    chat_id = int(req[1])

    if reserve:
        mrkp = types.InlineKeyboardMarkup()
        mrkp.add(types.InlineKeyboardButton(
            'Зарезервировать', callback_data='reserve'))
        red_bot.send_message(chat_id, msg, reply_markup=mrkp)
    else:
        red_bot.send_message(chat_id, msg)


##############################################################################


IS_TOKEN_WAIT = False

# START MESSAGE
@bot.message_handler(commands=['start'])
def welc(message):
    if not check_registration(message.chat.id):
        bot.send_message(message.chat.id, msg.lib_hello + msg.lib_token_help)
        global IS_TOKEN_WAIT
        IS_TOKEN_WAIT = True
    else:
        send_help(message)


# CHECK TOKEN AND REGISTRATE
@bot.message_handler(func=lambda message: IS_TOKEN_WAIT)
def text_handle(message):
    db = db_worker(config.db_path)
    if message.text in lib_tokens:
        db.add_librarian(int(message.chat.id), lib_tokens[message.text])
        bot.send_message(
            message.chat.id, 'Вы успешно зарегистрированы\n' + msg.lib_help)
        global IS_TOKEN_WAIT
        IS_TOKEN_WAIT = False
        logger.debug('user[{id}] : included to library', id = message.chat.id)
    else:
        bot.send_message(
            message.chat.id, msg.token_not_found)
    logger.debug('user[{id}] : mistake in library token', id = message.chat.id)
    


# HELP MESSAGE
@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, msg.lib_help)
    logger.debug('user[{id}] : take help message', id = message.chat.id)



##############################################################################

pgt = ''

# SEND REQUESTS LIST
@bot.message_handler(func=lambda message: message.text == '/get_all' 
                            and check_registration(message.chat.id))
def get_quer(message):
    logger.debug('user[{id}] : take requests list', id = message.chat.id)
    db = db_worker(config.db_path)
    requests = db.get_requests_for_librarian(message.chat.id)
    if len(requests):
        req = []
        for r in requests:
            rec = 'книга: '
            rec += r[2] + '\n' + r[4][:10] + '\n' + 'текущий ответ: ' + \
                   str(r[6]) + '\n' + 'номер запроса:' + str(r[0]) + '\n'
            req.append(rec)
        global pgt
        pgt = Paginator(req, REQUESTS_LIST_SPLIT, 
                        msg.tip_to_librarian_1)
        ms, mrkp = pgt.make_first_page()
        bot.send_message(message.chat.id, ms, reply_markup=mrkp)
    else:
        bot.send_message(message.chat.id, 'Запросов пока нет.')
    db.close()

# LEAFING REQUEST LIST
@bot.callback_query_handler(func=lambda click: click.data in ['next', 
                                                              'previous'])
def pagin_btns(click):
    global pgt
    if click.data == 'next':
        mess, mrkp = pgt.make_next_page()
        bot.edit_message_text(mess, message_id=click.message.message_id,
                              reply_markup=mrkp, chat_id=click.from_user.id)
    elif click.data == 'previous':
        mess, mrkp = pgt.make_previous_page()
        bot.edit_message_text(mess, message_id=click.message.message_id,
                              reply_markup=mrkp, chat_id=click.from_user.id)


##############################################################################
# WORK WITH ONE QUERY


# SEND ONE ITEM OF REQUESTS LIST
@bot.callback_query_handler(func=lambda click: click.data[:4] == 'item')
def one_query(click):
    logger.debug('user[{id}] : open one item in list', id = click.from_user.id)
    global pgt
    mess, mrkp = pgt.make_one(int(click.data[4])-1, 
                              ['вернуться к списку', 
                              'ответить', 
                              'удалить запрос'], 
                              ['back_to_list', 
                              'response', 
                              'del_req'])
    bot.edit_message_text(mess, message_id=click.message.message_id,
                          reply_markup=mrkp, chat_id=click.from_user.id)


# DELETE REQUEST
@bot.callback_query_handler(func=lambda click: click.data == 'del_req')
def del_req(click):
    book_n = click.message.text
    req_id = int(book_n[book_n.index('номер запроса:')+14:])
    db = db_worker(config.db_path)
    db.remove_request(req_id)
    db.close()
    mrkp = types.InlineKeyboardMarkup()
    mrkp.add(types.InlineKeyboardButton('Вернуться к списку запросов', 
                                        callback_data='update_list'))
    bot.edit_message_text(text='запрос удален', 
                          message_id=click.message.message_id,
                          chat_id=click.from_user.id, reply_markup=mrkp)
    logger.debug('user[{id}] : del query number {n}', n = req_id, id = click.from_user.id)


# BACK TO REQUESTS LIST
@bot.callback_query_handler(func=lambda click: click.data == 'back_to_list')
def back_to_list(click):
    global pgt
    mess, mrkp = pgt.make_first_page()
    bot.edit_message_text(mess, message_id=click.message.message_id,
                          reply_markup=mrkp, chat_id=click.from_user.id)
    logger.debug('user[{id}] : back to requests list', id = click.from_user.id)


# CHANGE KEYBOARD FOR ANSWER
@bot.callback_query_handler(func=lambda click: click.data == 'response')
def create_respone(click):
    mrkp = types.InlineKeyboardMarkup()
    mrkp.add(types.InlineKeyboardButton(msg.lib_ans_btn_sorry_no_book, 
                                        callback_data='book_unavailable'))
    mrkp.add(types.InlineKeyboardButton(msg.lib_ans_btn_book_avail, 
                                        callback_data='book_available'))

    bot.edit_message_reply_markup(
        click.from_user.id, click.message.message_id, reply_markup=mrkp)


# SEND POSITIVE ANSWER
@bot.callback_query_handler(lambda click: click.data == 'book_available')
def reserve_book(click):
    mes_txt = click.message.text
    req_id = int(mes_txt[mes_txt.index('номер запроса:')+14:])
    send_response_to_reader(msg.lib_ans_btn_book_avail,
                            req_id, True)

    db = db_worker(config.db_path)
    db.add_response(msg.lib_ans_btn_book_avail, req_id)
    db.close()
    mrkp = types.InlineKeyboardMarkup()
    mrkp.add(types.InlineKeyboardButton('Вернуться к списку запросов', 
                                        callback_data='update_list'))
    bot.edit_message_text('Ответ отправлен пользователю', click.from_user.id, click.message.message_id)
    bot.edit_message_reply_markup(click.from_user.id, click.message.message_id, reply_markup=mrkp)
    logger.debug('user[{id}] : + answer to request number {n}', n = req_id, id = click.from_user.id)


# SEND NEGATIVE ANSWER
@bot.callback_query_handler(lambda click: click.data == 'book_unavailable')
def send_sorry(click):
    book_n = click.message.text
    req_id = int(book_n[book_n.index('номер запроса:')+14:])
    book_n = book_n[book_n.index('книга:')+6:book_n.index('текущий ответ')-1]

    db = db_worker(config.db_path)
    r_chat_id = int(db.get_request_by_id(req_id)[1])
    db.remove_request(req_id)
    db.close()
    r_bot = telebot.TeleBot(config.U_BOT_TOKEN)
    mess = 'Ответ на ваш запрос:\n' + book_n + msg.lib_ans_book_unavail
    r_bot.send_message(r_chat_id, mess)
    mrkp = types.InlineKeyboardMarkup()
    mrkp.add(types.InlineKeyboardButton('Удалить запрос', 
                                        callback_data='del_req'))
    bot.edit_message_reply_markup(click.from_user.id, 
                                click.message.message_id, 
                                reply_markup=mrkp)
    logger.debug('user[{id}] : - answer to request number {n}', n = req_id, id = click.from_user.id)


# GENERATE NEW LIST AFTER WORKING WITH ONE REQUEST
@bot.callback_query_handler(func=lambda click: click.data == 'update_list')
def create_new_data_list(click):
    db = db_worker(config.db_path)
    requests = db.get_requests_for_librarian(click.from_user.id)
    req = []
    for r in requests:
        rec = 'книга: ' + r[2] + r[4][:10] + \
            '\n' + 'текущий ответ: ' + \
            str(r[6]) + '\n' + 'номер запроса: ' + str(r[0]) + '\n'
        req.append(rec)
    global pgt
    pgt = Paginator(req, 
                    REQUESTS_LIST_SPLIT, 
                    msg.tip_to_librarian_1)
    ms, mrkp = pgt.make_first_page()
    bot.send_message(click.from_user.id, ms, reply_markup=mrkp)
    db.close()
    logger.debug('user[{id}] : reload requests list', id = click.from_user.id)


##############################################################################
# LIBRARIAN ACCAUNT FUNCTIONS

# DEL
@bot.message_handler(func=lambda message: message.text == '/del_me' and 
                                          check_registration(message.chat.id))
def del_empl(message):
    db = db_worker(config.db_path)
    db.remove_librarian(message.chat.id)
    bot.send_message(message.chat.id, "Вы успешно удалены из системы")
    welc(message)
    logger.debug('user[{id}] : removed', id = message.chat.id)


# MUTE
@bot.message_handler(func=lambda message: message.text == '/mute' and 
                                          check_registration(message.chat.id))
def mute_us(message):
    db = db_worker(config.db_path)
    db.mute_librarian(message.chat.id)
    bot.send_message(message.chat.id, msg.lib_mute)

# UNMUTE
@bot.message_handler(func=lambda message: message.text == '/unmute' and
                                          check_registration(message.chat.id))
def unmute_us(message):
    db = db_worker(config.db_path)
    db.unmute_librarian(message.chat.id)
    bot.send_message(message.chat.id, msg.lib_unmute)


##############################################################################

@bot.message_handler(content_types=['text'])
def handle_other_cases(message):
    send_help(message)


if __name__ == "__main__":
    # libr_bot.polling()
    bot.polling(none_stop=True)
