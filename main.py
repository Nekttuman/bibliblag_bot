import time

import telebot
import config

import scrapper
EventSrc = 'https://biblioblag.ru/mibs/plan-meropriyatij'

if __name__ == "__main__":
# сам бот
    bot = telebot.TeleBot(config.TOKEN)

    @bot.message_handler(commands = ['start'])
    def welcome(message):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(telebot.types.KeyboardButton('Найти книгу'),
                   telebot.types.KeyboardButton('Узнать о мероприятиях'))
        bot.send_message(message.chat.id, 'Вас приветствует кибер-Чехов! С помощьюю данного бота вы можете:\nа) проверить наличие книги в библиотеке и зарезервировать её на получение в определенный срок\nб) узнать о предстоящих мероприятиях и записаться на них',
                            reply_markup=markup)


    BOOKFINDING = False   
    @bot.message_handler(content_types=['text'])
    def lol(message):
        if message.text == 'Найти книгу':
            bot.send_message(message.chat.id, 'Введите название книги и автора')
            BOOKFINDING = True
        elif BOOKFINDING:
            # Следует написать проверку ввода
            booksInfoMessage = scrapper.find_books(message.text)
            bot.send_message(message.chat.id, booksInfoMessage)
            BOOKFINDING = False
        
        if message.text == 'Узнать о мероприятиях':
            
            bot.send_message(message.chat.id, 'dd')
            
 

            

#     @bot.callback_query_handler(func=lambda call: True)
#     def callback_inline(call):
#         try:
#             if call.message:
#                 if call.data == 'find_book':
#                     bot.send_message(message.chat.id, 'Введите название книги')

    

   
#RUN
if __name__ == "__main__":
    bot.polling(none_stop=True)