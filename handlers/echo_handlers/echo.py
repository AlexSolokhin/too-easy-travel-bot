from loader import bot
from telebot.types import Message


@bot.message_handler(content_types=['text'], state=None)
def echo(message: Message) -> None:
    """
    Функция реакции на сообщение, не являющееся командой.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if message.text.lower().startswith('прив'):
        bot.send_message(message.chat.id,
                         "Привет! Я помогу тебе найти отели в любой точке мира! Чтобы узнать, что я умею, введи /help")
    else:
        bot.send_message(message.chat.id,
                         "К сожалению, я не понимаю человеческую речь.\n"
                         "Но зато могу помочь найти лучшие отели по всему миру!\n "
                         "Введи /help, чтобы узнать больше!")
