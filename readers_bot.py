import telebot
from telebot import types
import config
import msg
from scrapper import Scrapper
# import employee_bot
from paginator import Paginator


bot = telebot.TeleBot(config.U_BOT_TOKEN)
pgt = ''
scr = ''


def clear_last_session():
    global scr
    if not isinstance(scr, str):
        scr.close_browser()
    global pgt
    if not isinstance(pgt, str):
        pgt.clear_data()


@bot.message_handler(commands=['start'])
def welcome(message):
    bot.send_message(message.chat.id, msg.start_message)


# BOOK FINDING
BookFindingOn = False


@bot.message_handler(commands=['find_book'])
def start_book_find(message):
    bot.send_message(message.chat.id, msg.book_name,
                     parse_mode='markdown')
    global BookFindingOn
    BookFindingOn = True
    clear_last_session()

# тут где-то фильтры добавить

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
            pgt = Paginator(books, final_tip=msg.books_list_req_tip,
                            msg_chat_id=message.chat.id, split=3)
            mess, mrkp = pgt.make_first_page()
            bot.send_message(message.chat.id, mess, reply_markup=mrkp)
            BookFindingOn = False
        else:
            bot.send_message(message.chat.id, msg.not_found)
            scr.close_browser()
    else:
        bot.send_message(message.chat.id, 'Давай попробуем ещё раз')
        welcome(message)


# FOR PAGINATION
@bot.callback_query_handler(lambda click: click.data == 'next' or 
                            click.data == 'previous' or click.data[:4] == 'item')
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
        mess, mrkp = pgt.make_next_page()
        bot.edit_message_text(mess, message_id=click.message.message_id,
                              reply_markup=mrkp, chat_id=click.from_user.id)
    elif click.data == 'previous':
        mess, mrkp = pgt.make_previous_page()
        bot.edit_message_text(mess, message_id=click.message.message_id,
                              reply_markup=mrkp, chat_id=click.from_user.id)
    else:
        mess, mrkp = pgt.make_only(int(click.data[4]))
        bot.edit_message_text(mess, message_id=click.message.message_id,
                              reply_markup=mrkp, chat_id=click.from_user.id)


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

    # 993803709
