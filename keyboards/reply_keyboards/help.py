from telebot import types


def help_keyboard() -> types.ReplyKeyboardMarkup:
    """
    Создаёт клавиатуру с основными командами бота

    :return: keyboard
    :rtype: ReplyKeyboardMarkup
    """

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    lowprice = types.KeyboardButton('/lowprice')
    highprice = types.KeyboardButton('/highprice')
    bestdeal = types.KeyboardButton('/bestdeal')
    history = types.KeyboardButton('/history')
    favorites = types.KeyboardButton('/favorites')
    help_button = types.KeyboardButton('/help')
    keyboard.row(lowprice, highprice)
    keyboard.row(bestdeal)
    keyboard.row(history, favorites)
    keyboard.row(help_button)

    return keyboard
