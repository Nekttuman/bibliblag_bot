import time

import telebot
import config

import books_requests
    

if __name__ == "__main__":
# сам бот
    bot = telebot.TeleBot(config.TOKEN)

    @bot.message_handler(commands = ['start'])
    def welcome(message):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton('Найти книгу'),
                   telebot.types.KeyboardButton('Что нового в Чеховке?'))

        bot.send_message(message.chat.id, '''
Вас приветствует кибер-Чехов! С помощьюю данного бота вы можете:
а) проверить наличие книги в библиотеке и зарезервировать её на получение в определенный срок
б) узнать о предстоящих мероприятиях и записаться на них
        ''', reply_markup=markup)

    LISTEN = False
    @bot.message_handler(content_types=['text'])
    def lol(message):
        global LISTEN
        if message.chat.type == 'private':
            if message.text == 'Найти книгу':
                bot.send_message(message.chat.id, 'Введите название книги и автора')
                LISTEN = True
            elif LISTEN:
                s = message.text
                books_requests.find_books_in_browser(s)

                LISTEN = False



            


            

#     @bot.callback_query_handler(func=lambda call: True)
#     def callback_inline(call):
#         try:
#             if call.message:
#                 if call.data == 'find_book':
#                     bot.send_message(message.chat.id, 'Введите название книги')

    

   
#RUN
bot.polling(none_stop=True)