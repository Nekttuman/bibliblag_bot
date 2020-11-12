import telebot
from telebot import types
import config
import msg


bot = telebot.TeleBot(config.E_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def welc(message):
    print(message.chat.id)
    bot.send_message(message.chat.id,'hehe')

def send_smth(chat_id, mes):
    bot.send_message(chat_id, mes)

if __name__ == "__main__":
    # libr_bot.polling()
    bot.polling(none_stop=True)