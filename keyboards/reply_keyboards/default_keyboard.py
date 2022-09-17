from telebot import types


def default_keyboard() -> types.ReplyKeyboardMarkup:
    """
    Создаёт стандартную reply-клавиатуру с возможностью остановить или перезапустить поиск.

    :return: keyboard
    :rtype: ReplyKeyboardMarkup
    """

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    try_again = types.KeyboardButton('Начать сначала')
    stop_search = types.KeyboardButton('Прервать поиск')

    keyboard.row(try_again, stop_search)

    return keyboard
