from loader import bot
from keyboards.reply_keyboards.help import help_keyboard


@bot.message_handler(commands=['start', 'hello-world'])
def greetings(message):
    """
    Функция-приветствие (команда start и hello-world)

    :param message: объект сообщения
    """
    bot.send_message(message.chat.id, 'Привет! Я помогу тебе найти лучшие отели по всему миру. '
                                      'Чтобы начать, введи команду или введи /help для справки!',
                     reply_markup=help_keyboard())
