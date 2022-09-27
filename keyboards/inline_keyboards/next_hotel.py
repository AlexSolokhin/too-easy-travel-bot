from telebot import types


def next_hotel_keyboard(text: str, method: str, page_num: int, hotel_num: int) -> types.InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для вызова следующего отеля.

    :param text: Текст кнопки
    :type text: str
    :param method: Метод, вызываемый кнопкой
    :type method: str
    :param page_num: номер страницы
    :type page_num: int
    :param hotel_num: номер отеля
    :type hotel_num: int
    :return: keyboard
    :rtype: InlineKeyboardMarkup
    """

    keyboard = types.InlineKeyboardMarkup()

    show_hotel = types.InlineKeyboardButton(text=text,
                                            callback_data=
                                            '{"method":"' + method +
                                            '","page_num":' + str(page_num) +
                                            ',"hotel_num":' + str(hotel_num + 1) +
                                            '}'
                                            )
    try_again = types.InlineKeyboardButton(text='↩Начать сначала', callback_data='TRY_AGAIN')
    stop_search = types.InlineKeyboardButton(text='🛑Прервать поиск', callback_data='CANCEL')

    keyboard.add(show_hotel)
    keyboard.add(try_again)
    keyboard.add(stop_search)

    return keyboard
