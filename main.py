# coding: cp1251
import telebot
import sqlite3
from sqlite3 import Error

bot = telebot.TeleBot('YOUR_TOKEN')


def create_connection(path):
    con = None
    try:
        con = sqlite3.connect(path, check_same_thread=False)
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return con


connection = create_connection('ApartBot.ewrey_db')
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS apartaments (adress text, user text, description text)")


def addApart(adress, userId):
    cursor.execute("INSERT INTO apartaments (user, adress) VALUES (?, ?)", [str(userId), adress])
    connection.commit()


def getAparts(userId):
    cursor.execute("SELECT adress FROM apartaments WHERE user=:id", {"id": userId})
    connection.commit()


def apartInTable(url, userId):
    cursor.execute("SELECT user FROM apartaments WHERE adress=:url", {"id": userId, "url": url})
    connection.commit()
    return str(cursor.fetchone()).__contains__(str(userId))


def apartHasDescription(userId, url):
    cursor.execute("SELECT description FROM apartaments WHERE adress=:url AND user=:id", {"id": userId, "url": url})
    return not str(cursor.fetchone()).__contains__('None')


def getDescription(userId, url):
    cursor.execute("SELECT description FROM apartaments WHERE adress=:url AND user=:id", {"id": userId, "url": url})
    return str(cursor.fetchone())[1:].replace(',)', '')


def addDescription(userId, url, description):
    cursor.execute("UPDATE apartaments SET description=:desc WHERE user=:user AND adress=:url",
                   {"desc": description, "user": userId, "url": url})
    connection.commit()


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    chatId = message.chat.id
    text = str(message.text)
    if text.startswith('/p'):
        adress = text[text.index(' ') + 1:]
        print(adress)
        print(chatId)
        try:
            addApart(adress, chatId)
            bot.send_message(message.from_user.id, 'Адрес добавлен')
        except Exception as e:
            bot.send_message(message.from_user.id, f'Адрес не добавлен ошибка - {e}')
        # getAparts(chatId)
    elif text.startswith('/desc'):
        url = text[text.index('[') + 1: text.index(']')]
        desc = text[text.index('(') + 1:text.index(')')]
        addDescription(userId=chatId, url=url, description=desc)
    elif text.startswith('http'):
        if apartInTable(text, chatId):
            bot.send_message(message.from_user.id, 'Вы смотрели этот вариант')
            if not apartHasDescription(userId=chatId, url=text):
                bot.send_message(message.from_user.id, 'Вы не добавили описания квартиры, можете сделать это  \
                                                       с помощью /desc [ваш_url] (ваше_описание)')
            else:
                bot.send_message(message.from_user.id, f'Ваше описание : \n{getDescription(userId=chatId, url=text)}')
        else:
            bot.send_message(message.from_user.id, 'Вы не смотрели этот вариант, для добавления введите /p вашу_ссылку')
    else:
        bot.send_message(chatId, f"Привет {message.from_user.first_name}, я бот помогающий сохранять квартиры в "
                                 f"закладки, дабы повторно не проверять одни и те же квартиры, а так же, "
                                 f"вы можете сохранить свое описание для квартиры")


bot.polling(none_stop=True, interval=0)