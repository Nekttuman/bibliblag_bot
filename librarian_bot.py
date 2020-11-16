import telebot
from telebot import types
import config
import msg
from db.lib_tokens import lib_tokens
from db.db_worker import db_worker



bot = telebot.TeleBot(config.E_BOT_TOKEN)

IS_REGISTRATED = False
IS_TOKEN_WAIT = False
@bot.message_handler(commands=['start'])
def welc(message):
    db = db_worker('db/libra.db')
    global IS_REGISTRATED
    IS_REGISTRATED = db.check_librarian(message.chat.id)
    if not IS_REGISTRATED:
        bot.send_message(message.chat.id, msg.lib_hello + msg.lib_token_help)
        global IS_TOKEN_WAIT
        IS_TOKEN_WAIT = True
    else:
        bot.send_message(message.chat.id, msg.lib_help)

@bot.message_handler(commands = ['get_all'])
def get_quer(message):
    db = db_worker('db/libra.db')
    if db.check_librarian(message.chat.id):
        requests = db.get_requests(message.chat.id)
        print(requests)
        # bot.send_message(message.chat.id, requests)
    else:
        welc(message)

@bot.message_handler(commands=['del_me'])
def del_empl(message):
    db = db_worker('db/libra.db')
    if db.check_librarian(message.chat.id):
        db.remove_librarian(message.chat.id)
        bot.send_message(message.chat.id, "Вы успешно удалены из системы")
    else:
        welc(message)

@bot.message_handler(commands=['mute'])
def mute_us(message):
    db = db_worker('db/libra.db')
    if db.check_librarian(message.chat.id):
        db.mute_librarian(message.chat.id)
    else:
        welc(message)

@bot.message_handler(commands=['unmute'])
def unmute_us(message):
    db = db_worker('db/libra.db')
    if db.check_librarian(message.chat.id):
        db.unmute_librarian(message.chat.id)
    else:
        welc(message)

@bot.message_handler(content_types=['text'])
def text_handle(message):
    global IS_TOKEN_WAIT
    global IS_REGISTRATED
    db = db_worker('db/libra.db')
    if IS_TOKEN_WAIT:
        if message.text in lib_tokens:
            db.add_librarian(int(message.chat.id), lib_tokens[message.text])
            bot.send_message(message.chat.id, 'Вы успешно зарегистрированы\n' + msg.lib_help)
            IS_TOKEN_WAIT = False
            IS_REGISTRATED = True
        else:
            bot.send_message(message.chat.id, 'Токен не найден, проверьте правильность написания и повторите попытку')
    else: 
        if IS_REGISTRATED:
            bot.send_message(message.chat.id, msg.lib_help)
        else:
            bot.send_message(message.chat.id, msg.lib_token_help)
            IS_TOKEN_WAIT = True


def send_smth(chat_id, mes):
    bot.send_message(chat_id, mes)

if __name__ == "__main__":
    # libr_bot.polling()
    bot.polling(none_stop=True)