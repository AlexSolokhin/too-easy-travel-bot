from telebot import types


def location_type_keyboard() -> types.InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для выбора типа локации

    :return: keyboard
    :rtype: InlineKeyboardMarkup
    """

    keyboard = types.InlineKeyboardMarkup()

    city_group = types.InlineKeyboardButton(text='В городе', callback_data='CITY_GROUP')
    landmark_group = types.InlineKeyboardButton(text='Рядом с достопримечательностью', callback_data='LANDMARK_GROUP')
    transport_group = types.InlineKeyboardButton(text='Рядом с вокзалом, аэропортом, транспортным узлом',
                                                 callback_data='TRANSPORT_GROUP')
    stop_search = types.InlineKeyboardButton(text='Прервать поиск', callback_data='CANCEL')

    keyboard.add(city_group)
    keyboard.add(landmark_group)
    keyboard.add(transport_group)
    keyboard.add(stop_search)
    return keyboard
