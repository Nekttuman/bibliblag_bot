import telebot
from telebot import types
import config
import msg
from db.lib_tokens import lib_tokens
from db.db_worker import db_worker
from paginator import Paginator
import pickledb
from readers_bot import send_response_to_reader


bot = telebot.TeleBot(config.E_BOT_TOKEN)
req_id_db = pickledb.load('readers_states.db', False)

REQUESTS_LIST_SPLIT = 4


def check_registration(chat_id):
    db = db_worker(config.db_path)
    return db.check_librarian(chat_id)


IS_TOKEN_WAIT = False
######################################################################################
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
@bot.message_handler(func = lambda message: IS_TOKEN_WAIT)
def text_handle(message):
    db = db_worker(config.db_path)
    if message.text in lib_tokens:
        db.add_librarian(int(message.chat.id), lib_tokens[message.text])
        bot.send_message(
            message.chat.id, 'Вы успешно зарегистрированы\n' + msg.lib_help)
        global IS_TOKEN_WAIT
        IS_TOKEN_WAIT = False
    else:
        bot.send_message(
            message.chat.id, 'Токен не найден, проверьте правильность написания и повторите попытку')

# HELP MESSAGE

@bot.message_handler(commands=['help'])
def send_help(message):
    bot.send_message(message.chat.id, msg.lib_help)

pgt = ''

######################################################################################
# SEND REQUESTS LIST

@bot.message_handler(func=lambda message: message.text == '/get_all' and check_registration(message.chat.id))
def get_quer(message):
    db = db_worker(config.db_path)
    requests = db.get_requests(message.chat.id)
    if len(requests):
        req = []
        for r in requests:
            rec = 'читатель: ' + r[2] + '\n' + 'книга: ' + r[3] + '\n' + r[5][:10] + \
                '\n' + 'id запроса: ' + \
                str(r[0]) + '\n' + 'текущий ответ: ' + str(r[7]) + '\n'
            req.append(rec)
        global pgt
        pgt = Paginator(
            req, REQUESTS_LIST_SPLIT, 'Чтобы ответить читателю, нажмите на кнопку с номером его запроса')
        ms, mrkp = pgt.make_first_page()
        bot.send_message(message.chat.id, ms, reply_markup=mrkp)
    else:
        bot.send_message(message.chat.id, 'Запросов пока нет.')
    db.close()
    # bot.send_message(message.chat.id, requests)


@bot.callback_query_handler(func=lambda click: click.data in ['next', 'previous'])
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


@bot.callback_query_handler(func=lambda click: click.data[:4] == 'item')
def one_query(click):
    global pgt
    mess, mrkp = pgt.make_one(int(click.data[4])-1, ['вернуться к списку',
                                                     'ответить', 'удалить запрос'], ['back_to_list', 'response', 'del_quer'])
    bot.edit_message_text(mess, message_id=click.message.message_id,
                          reply_markup=mrkp, chat_id=click.from_user.id)
    req_id = pgt.get_item(int(click.data[4])-1)
    req_id = req_id[req_id.index('са: ')+4: req_id.index('теку')]
    req_id_db.set(str(click.from_user.id), req_id)


@bot.callback_query_handler(func=lambda click: click.data == 'back_to_list')
def back_to_list(click):
    global pgt
    mess, mrkp = pgt.make_first_page()
    bot.edit_message_text(mess, message_id=click.message.message_id,
                          reply_markup=mrkp, chat_id=click.from_user.id)


######################################################################################
# WORK WITH ONE QUERY

IS_WAIT_RESPONSE = False

@bot.callback_query_handler(func=lambda click: click.data[:8] == 'response')
def create_respone(click):
    bot.send_message(click.from_user.id, 'Введите ваш ответ пользователю')
    global IS_WAIT_RESPONSE
    IS_WAIT_RESPONSE = True


@bot.message_handler(func=lambda message: IS_WAIT_RESPONSE and message.text[0] != '/')
def set_response(message):
    db = db_worker(config.db_path)
    global IS_WAIT_RESPONSE
    IS_WAIT_RESPONSE = False
    req_id = int(req_id_db.get(str(message.chat.id)))
    db.add_response(message.text, req_id)
    db.close()
    mrkp = types.InlineKeyboardMarkup()
    mrkp.add(types.InlineKeyboardButton('Вернуться к списку запросов', callback_data='update_list'))
    bot.send_message(message.chat.id, 'Ответ отправлен', reply_markup=mrkp)

@bot.callback_query_handler(func=lambda click: click.data == 'update_list')
def create_new_data_list(click):
    db = db_worker(config.db_path)
    requests = db.get_requests(click.from_user.id)
    req = []
    for r in requests:
        rec = 'читатель: ' + r[2] + '\n' + 'книга: ' + r[3] + '\n' + r[5][:10] + \
            '\n' + 'id запроса: ' + \
            str(r[0]) + '\n' + 'текущий ответ: ' + str(r[7]) + '\n'
        req.append(rec)
    global pgt
    pgt = Paginator(
        req, REQUESTS_LIST_SPLIT, 'Чтобы ответить читателю, нажмите на кнопку с номером его запроса')
    ms, mrkp = pgt.make_first_page()
    bot.send_message(click.from_user.id, ms, reply_markup=mrkp)
    db.close()

@bot.callback_query_handler(func=lambda click: click.data == 'del_quer')
def del_quer(click):
    print(click)
    db = db_worker(config.db_path)
    db.remove_request(int(req_id_db.get(str(click.from_user.id))))
    req_id_db.rem(str(click.from_user.id))
    mrkp = types.InlineKeyboardMarkup()
    mrkp.add(types.InlineKeyboardButton(
        'Вернуться к списку запросов', callback_data='update_list'))
    bot.edit_message_text('этот запрос удален', message_id=click.message.message_id,
                          chat_id=click.from_user.id, reply_markup=mrkp)

######################################################################################
# LIBRARIAN ACCAUNT FUNCTIONS

# DEL 

@bot.message_handler(func=lambda message: message.text == '/del_me' and check_registration(message.chat.id))
def del_empl(message):
    db = db_worker(config.db_path)
    db.remove_librarian(message.chat.id)
    bot.send_message(message.chat.id, "Вы успешно удалены из системы")
    welc(message)


# MUTE
@bot.message_handler(func=lambda message: message.text == '/mute' and check_registration(message.chat.id))
def mute_us(message):
    db = db_worker(config.db_path)
    db.mute_librarian(message.chat.id)
    bot.send_message(message.chat.id, msg.lib_mute)

# UNMUTE
@bot.message_handler(func=lambda message: message.text == '/unmute' and check_registration(message.chat.id))
def unmute_us(message):
    db = db_worker(config.db_path)
    db.unmute_librarian(message.chat.id)
    bot.send_message(message.chat.id, msg.lib_unmute)


######################################################################################

@bot.message_handler(content_types = ['text'])
def handle_other_cases(message):
    send_help(message)



def send_real_time_req(chat_id):
    pass


if __name__ == "__main__":
    # libr_bot.polling()
    bot.polling(none_stop=True)
