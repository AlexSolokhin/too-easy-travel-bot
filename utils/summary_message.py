from loader import bot
import re
from database.history_db_methods import add_history_to_db
from keyboards.inline_keyboards.next_hotel import next_hotel_keyboard


def summary_message_handler(search_data: dict, chat_id: int) -> None:
    """
    Генерация и отправка сообщения, в котором собраны все данные, переданные пользователем.
    Также сохраняет детали гтового заброса в бд.

    :param search_data: словарь с данными, переданными пользователем
    :type search_data: dict
    :param chat_id: id чата с пользователем
    :type chat_id: int
    :return: None
    """

    command = search_data['command']
    location = search_data["location"]
    check_in = search_data["checkin_date"].strftime("%d-%m-%Y")
    check_out = search_data["checkout_date"].strftime("%d-%m-%Y")
    min_price = search_data.get('min_price', None)
    max_price = search_data.get('max_price', None)
    min_dist = search_data.get('min_dist', None)
    max_dist = search_data.get('max_dist', None)

    filters_string = ''

    if command == 'lowprice':
        category_string = 'самые дешёвые отели'
    elif command == 'highprice':
        category_string = 'самые дорогие отели'
    else:
        category_string = 'отели с учётом цены и расстояния от центра города'
        filters_string = f'\n*Минимальная цена за ночь:* {min_price} рублей\n' \
                         f'*Максимальная цена за ночь*: {max_price} рублей\n' \
                         f'*Минимальное расстояние от центра*: {min_dist} км\n' \
                         f'*Максимальное расстояние от центра*: {max_dist} км'

    summary_message = f'Итак, мы ищем *{category_string}* в локации: *{location}*\n' \
                      f'*Дата заезда:* {check_in}\n' \
                      f'*Дата выезда:* {check_out}' \
                      f'{filters_string}'

    summary_message = re.sub(r'-', r'[\-]', summary_message)
    summary_message = re.sub(r'[.]', r'[\.]', summary_message)
    summary_message = re.sub(r'[(]', r'[\(]', summary_message)
    summary_message = re.sub(r'[)]', r'[\)]', summary_message)

    bot.send_message(chat_id, summary_message, parse_mode='MarkdownV2')
    add_history_to_db(chat_id, command, location, check_in, check_out, min_price, max_price, min_dist, max_dist)

    bot.send_message(chat_id, 'Погнали?',
                     reply_markup=next_hotel_keyboard('😎Поехали!', 'INIT', 1, -1))
