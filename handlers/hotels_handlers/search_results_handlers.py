from loader import bot
import json
import re
from datetime import datetime
from telebot.types import CallbackQuery, InputMediaPhoto
from handlers.API_handlers import request_hotels
from handlers.API_handlers import request_photo
from states.travel_information import TravelInfoState
from database.history_db_methods import add_history_to_db, add_hotels_to_history_db
from keyboards.reply_keyboards.default_keyboard import default_keyboard
from keyboards.inline_keyboards.next_hotel import next_hotel_keyboard
from utils.show_hotels import show_hotel


def summary_message_handler(search_data: dict, chat_id: int) -> None:
    """
    Генерация и отправка сообщения, в котором собраны все данные, переданные пользователем.
    Также сохраняет детали заброса в бд.

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
                     reply_markup=next_hotel_keyboard('Поехали!', 'INIT', 1, -1))


@bot.callback_query_handler(func=lambda call: call.data.startswith('{'),
                            state=TravelInfoState.show_hotels)
def results_handler(callback: CallbackQuery) -> None:
    """
    Выдача отелей по одному.
    Сохранение выданных отелей в бд для истории поиска.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """
    chat_id = callback.message.chat.id
    bot.delete_message(chat_id, callback.message.id)

    callback_json = json.loads(callback.data)
    method = callback_json['method']
    page_num = callback_json['page_num']
    hotel_num = callback_json['hotel_num']

    with bot.retrieve_data(callback.from_user.id, chat_id) as data:
        if method == 'INIT':
            data['hotels_list'] = request_hotels(data, page_num)
        hotels_list = data['hotels_list']

    hotels_list_length = len(hotels_list)

    if hotels_list_length == 0:
        bot.send_message(chat_id, 'К сожалению, по твоему запросу не найдено ни одного отеля. Хочешь повторить поиск?',
                                  reply_markup=default_keyboard())

    elif hotels_list_length == hotel_num + 1 and hotel_num != 24:
        bot.send_message(chat_id, 'Отелей больше нет. Хочешь повторить поиск?',
                                  reply_markup=default_keyboard())

    else:
        add_hotels_to_history_db(chat_id, hotels_list[hotel_num]['id'], hotels_list[hotel_num]['name'])
        show_hotel(hotels_list[hotel_num], chat_id)

        if hotel_num == 24:
            page_num += 1
            hotel_num = 0
            with bot.retrieve_data(callback.from_user.id, chat_id) as data:
                data['hotels_list'] = request_hotels(data, page_num)

        bot.send_message(chat_id, 'Показать ещё?',
                         reply_markup=next_hotel_keyboard('Ещё!', 'NEXT', page_num, hotel_num))

    bot.answer_callback_query(callback.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('PHOTO'))
def show_hotel_photo(callback: CallbackQuery) -> None:
    """
    Выдача фото отеля.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """

    hotel_id = int(callback.data.split('|')[1])
    photos_list = request_photo(hotel_id)

    media_list = []

    for i_photo in photos_list:
        input_media = InputMediaPhoto(i_photo, caption='hi')
        media_list.append(input_media)

    bot.send_media_group(callback.message.chat.id, media_list)

    bot.answer_callback_query(callback.id)


@bot.callback_query_handler(func=lambda call: call.data == 'HIDE',
                            state=TravelInfoState.show_hotels)
def hide_hotel(callback: CallbackQuery) -> None:
    """
    Удаление отеля из чата.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """

    bot.delete_message(callback.message.chat.id, callback.message.id)

    bot.answer_callback_query(callback.id)

# TODO - заменить default_keyboard: reply на inline
