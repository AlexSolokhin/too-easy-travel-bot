from telebot import types


def simple_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    stop_search = types.KeyboardButton('Прервать поиск')
    keyboard.add(stop_search)
    return keyboard


def yes_no_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    yes = types.KeyboardButton('Да')
    no = types.KeyboardButton('Нет')
    stop_search = types.KeyboardButton('Прервать поиск')
    keyboard.row(yes, no)
    keyboard.row(stop_search)
    return keyboard


def one_to_ten_keybord():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    one = types.KeyboardButton('1')
    two = types.KeyboardButton('2')
    three = types.KeyboardButton('3')
    four = types.KeyboardButton('4')
    five = types.KeyboardButton('5')
    six = types.KeyboardButton('6')
    seven = types.KeyboardButton('7')
    eight = types.KeyboardButton('8')
    nine = types.KeyboardButton('9')
    ten = types.KeyboardButton('10')
    stop_search = types.KeyboardButton('Прервать поиск')
    keyboard.row(one, two, three, four, five, six, seven, eight, nine, ten)
    keyboard.row(stop_search)
    return keyboard


def help_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    lowprice = types.KeyboardButton('/lowprice')
    highprice = types.KeyboardButton('/highprice')
    bestdeal = types.KeyboardButton('/bestdeal')
    history = types.KeyboardButton('/history')
    help_button = types.KeyboardButton('/help')
    keyboard.row(lowprice, highprice)
    keyboard.row(bestdeal)
    keyboard.row(history)
    keyboard.row(help_button)
    return keyboard
