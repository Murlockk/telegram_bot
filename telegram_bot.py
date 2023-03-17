import telebot
import time
from telebot import types

from main import main_func
from utils import PopularCoin, ConvertionException
from config import TOKEN, support_text, remark


bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message: telebot.types.Message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("BTC - USD")
    btn2 = types.KeyboardButton("ETH - USD")
    btn3 = types.KeyboardButton("USD - RUB")
    btn4 = types.KeyboardButton("EUR - RUB")
    btn5 = types.KeyboardButton("conversion_info")
    markup.add(btn5, btn1, btn2, btn3, btn4)
    text = f'👋 Здравствуйте, {message.from_user.first_name}! Чтобы начать работу с конвертором валют введите команду ' \
           f'боту в удобном Вам формате. \nИспользуйте общепринятые названия или обозначения валют и криптовалют.\n' \
           f'Имеются проблемы с вводом: используйте /help ' \
           f'Посмотреть популярные монеты: используйте /values'
    bot.reply_to(message, text, reply_markup=markup)


@bot.message_handler(commands=['values'])
def values(message: telebot.types.Message):
    bot.reply_to(message, PopularCoin.values_func())


@bot.message_handler(commands=['help'])
def values(message: telebot.types.Message):
    text = support_text + remark
    bot.reply_to(message, text)


@bot.message_handler(content_types=['text'])
def convert(message: telebot.types.Message):
    if message.text == "BTC - USD":
        text = "BTC - USD"
    elif message.text == "ETH - USD":
        text = "ETH - USD"
    elif message.text == "USD - RUB":
        text = "USD - RUB"
    elif message.text == "EUR - RUB":
        text = "EUR - RUB"
    elif message.text == "conversion_info":
        text = "more"
    else:
        text = message.text
    compilation = text.split(' ')
    try:
        result = main_func(compilation)
        if type(result) == list:
            info_func(message, result)
        else:
            bot.send_message(message.chat.id, result)
    except ConvertionException as er:
        bot.send_message(message.chat.id, str(er))


def info_func(message: telebot.types.Message, result):
    if result[0] in PopularCoin.keys.keys():
        text = f'На графике показано ориентировочное изменение рыночной стоимости {result[0]} в долларах США за ' \
               f'последние 7 дней'
        bot.send_photo(message.chat.id,
                       f'https://images.cryptocompare.com/sparkchart/{result[0]}/USD/latest.png?ts=1677232800')
    else:
        text = 'График изменения стоимости за 7 дней не доступен для денежных валют'  # Источник с jpeg не найден
    bot.send_message(message.chat.id, text)
    for _ in range(4):
        bot.send_message(message.chat.id, result.pop())


while True:
    try:
        bot.polling(none_stop=True)

    except Exception as e:
        print(e)
        time.sleep(5)
