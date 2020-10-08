import time

from selenium import webdriver
from selenium.webdriver.support.ui import Select

import telebot
import config





def find_books(req_str = ''):
    # Открываем окружение, находим все нужные элементы с помощью webdriver
    driver = webdriver.Chrome()
    driver.get("http://85.88.171.2:8080/cgi-bin/irbis64r_plus/cgiirbis_64_ft.exe?C21COM=F&I21DBN=KRAJ_FULLTEXT&P21DBN=KRAJ&Z21ID=&S21CNR=5")
    submit_button = driver.find_element_by_css_selector('[value="Войти как Гость"]')
    submit_button.click()
    print(submit_button)
    select = Select(driver.find_element_by_css_selector("[name='I21DBN']"))
    select.select_by_visible_text('Основной электронный каталог')
    search = driver.find_element_by_css_selector("#SEARCH_STRING")
    # Отправляем запрос
    search.send_keys(req_str)
    driver.find_element_by_name("C21COM1").click()
    time.sleep(10)
    driver.quit()
    

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
                find_books(s)

                LISTEN = False



            


            

#     @bot.callback_query_handler(func=lambda call: True)
#     def callback_inline(call):
#         try:
#             if call.message:
#                 if call.data == 'find_book':
#                     bot.send_message(message.chat.id, 'Введите название книги')

    

   
#RUN
bot.polling(none_stop=True)