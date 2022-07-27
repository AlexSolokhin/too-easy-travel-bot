import telebot
import sqlite3
import db_manage
from Dialog_Handler import Dialog
from datetime import datetime
from keybords import help_keyboard

bot = telebot.TeleBot('5445705971:AAFlMNKFBNwwuIszJc_zNbrj9JNJop2OJDg')


@bot.message_handler(commands=['start', 'hello-world'])
def greetings(message):
    """
    Функция-приветствие (команда start и hello-world)

    :param message: объект сообщения
    """
    bot.send_message(message.chat.id, 'Привет! Я помогу тебе найти лучшие отели по всему миру. '
                                      'Чтобы начать, введи команду или введи /help для справки!',
                     reply_markup=help_keyboard())


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def start_searching(message):
    """
    Функция создаёт экземпляр класса Dialog и запускает работу команд /lowprice, /highprice, /bestdeal.

    :param message: объект сообщения
    """
    try:
        dialog = Dialog(message)
        dialog(message, bot)
    except (Exception, sqlite3.Error) as error:
        with open('errors.log', 'a', encoding='utf-8') as error_log:
            error_log.write(f'{datetime.now()}\n{message}\n{message.from_user.id}\n{type(error)}\n{error}\n\n')
        bot.send_message(message.chat.id, 'Упс! При выполнении команды произошла ошибка.\n'
                                          'Попробуй ещё раз или напиши автору (@Alex Solokhin)')


@bot.message_handler(commands=['help'])
def help_command(message):
    """
    Функция справка (команда /help)

    :param message:
    """
    bot.send_message(message.chat.id, "Вот, что я умею:\n"
                                      "\n"
                                      "/lowprice: покажу топ самых дешевых отелей по выбранному направлению\n"
                                      "/highprice: покажу топ самых дорогих отелей по выбранному направлению\n"
                                      "/bestdeal: покажу топ предложений по вашему запросу (близость к центру, цена)\n"
                                      "/history: выдам историю твоего поиска\n"
                                      "/help: повторный вывод справки по командам", reply_markup=help_keyboard())


@bot.message_handler(commands=['history'])
def history_command(message):
    """
    Функция выдаёт историю поиска (команда /history)

    :param message: объект сообщения
    """
    try:
        history_query = '''SELECT `date_time`, `command`, `hotels_found`
        FROM user_requests WHERE `user_id` = ?'''
        user_id = message.from_user.id

        history_list = db_manage.get_all_lines(history_query, (user_id, ))
        if len(history_list) == 0:
            history_message = 'Ты ещё не сделал ни одного запроса. Чтобы узнать доступные команды, введи /help.'
        else:
            history_message = 'История ваших запросов:\n\n'

            for record in history_list:
                date = record[0][:16]
                record_message = '{date}\t Команда: {command}\nБыли найдены эти отели: {hotel_list}\n\n'.format(
                    date=date,
                    command=record[1],
                    hotel_list=record[2])
                history_message += record_message

        bot.send_message(message.chat.id, history_message)

    except Exception as error:
        with open('errors.log', 'a', encoding='utf-8') as error_log:
            error_log.write(f'{datetime.now()}\n{message}\n{message.from_user.id}\n{type(error)}\n{error}\n\n')
        print(error)
        bot.send_message(message.chat.id, 'Упс! При выполнении команды произошла ошибка.\n'
                                          'Попробуй ещё раз или напиши автору (@Alex Solokhin)')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    """
    Функция реакции на сообщение, не являющееся командой.

    :param message: объект сообщения
    """
    if message.text.lower().startswith('прив'):
        bot.send_message(message.chat.id,
                         "Привет! Я помогу тебе найти отели в любой точке мира! Чтобы узнать, что я умею, введи /help")
    else:
        bot.send_message(message.chat.id,
                         "К сожалению, я не понимаю человеческую речь. "
                         "Но зато могу помочь найти лучшие отели по всему миру. Введи /help, чтобы узнать больше!")


bot.polling(none_stop=True, interval=0)
