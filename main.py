import time

import telebot
import config
import msg
import scrapper


bot = telebot.TeleBot(config.TOKEN)

@bot.message_handler(commands = ['start'])
def welcome(message):
    bot.send_message(message.chat.id, msg.start_message)
          
 
#BOOK FINDING
get_book = False
addition_info = False
@bot.message_handler(commands =['find_book'])            
def search_book(message):
    bot.send_message(message.chat.id, msg.name_author_format, parse_mode='markdown')
    global get_book
    get_book = True
    
@bot.message_handler(content_types = ['text'])
def get_book(message):
    if get_book:
        author, name = message.text.split(' - ')
        scrapper.find_books(name + ' ' + author)
    else:
        bot.send_message(message.chat.id, msg.other_input)
        




@bot.message_handler(commands =['events'])
def  events(message):
    bot.send_message(message.chat.id, msg.start_message)
    

    
   
#RUN
if __name__ == "__main__":
    bot.polling(none_stop=True)