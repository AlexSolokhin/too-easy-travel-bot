from loader import bot
from keyboards.reply_keyboards.help import help_keyboard


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
    