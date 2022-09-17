import json
from loader import bot
from datetime import datetime
from telebot.types import CallbackQuery, InputMediaPhoto
from handlers.API_handlers import request_hotels
from handlers.API_handlers import request_photo
from states.travel_information import TravelInfoState
from keyboards.reply_keyboards.default_keyboard import default_keyboard
from keyboards.inline_keyboards.next_hotel import next_hotel_keyboard
from keyboards.inline_keyboards.hotel_details import hotel_details_keyboard


def summary_message_handler(search_data: dict, chat_id: int) -> None:
    """
    Генерация и отправка сообщения, в котором собраны все данные, переданные пользователем.

    :param search_data: словарь с данными, переданными пользователем
    :type search_data: dict
    :param chat_id: id чата с пользователем
    :type chat_id: int
    :return: None
    """

    filters_string = ''

    if search_data['command'] == 'lowprice':
        category_string = 'самые дешёвые отели'
    elif search_data['command'] == 'highprice':
        category_string = 'самые дорогие отели'
    else:
        category_string = 'отели с учётом цены и расстояния от центра города'
        filters_string = f'\nМинимальная цена за ночь: {search_data["min_price"]} рублей\n' \
                         f'Максимальная цена за ночь: {search_data["max_price"]} рублей\n' \
                         f'Минимальное расстояние от центра: {search_data["min_dist"]}\n км' \
                         f'Максимальное расстояние от центра: {search_data["max_dist"]} км'

    summary_message = f'Итак, мы ищем {category_string} в локации: {search_data["location"]}\n' \
                      f'Дата заезда: {search_data["checkin_date"].strftime("%d-%m-%Y")}\n' \
                      f'Дата выезда: {search_data["checkout_date"].strftime("%d-%m-%Y")}' \
                      f'{filters_string}'

    bot.send_message(chat_id, summary_message)
    bot.send_message(chat_id, 'Погнали?',
                     reply_markup=next_hotel_keyboard('Поехали!', 'INIT', 1, -1))


@bot.callback_query_handler(func=lambda call: call.data.startswith('{'),
                            state=TravelInfoState.show_hotels)
def results_handler(callback: CallbackQuery) -> None:
    """
    Выдача отелей по одному.

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
        show_hotel(hotels_list[hotel_num], chat_id)
        if hotel_num == 24:
            page_num += 1
            hotel_num = 0
            with bot.retrieve_data(callback.from_user.id, chat_id) as data:
                data['hotels_list'] = request_hotels(data, page_num)

        bot.send_message(chat_id, 'Показать ещё?',
                         reply_markup=next_hotel_keyboard('Ещё!', 'NEXT', page_num, hotel_num))

    bot.answer_callback_query(callback.id)


def show_hotel(hotel: dict, chat_id: int) -> None:
    """
    Выдача информации по отелю.

    :param hotel: словарь отеля
    :type hotel: dict
    :param chat_id: id чата
    :type chat_id: int
    :return: None
    """

    hotel_name = hotel['name']
    country = hotel['address'].get('countryName')
    city = hotel['address'].get('locality')
    street_adr = hotel['address'].get('streetAddress', 'Полный адрес доступен после бронирования.')
    distance = hotel['from_center']
    price_per_night = hotel['price']
    total_price = hotel['total_price']
    hotel_id = hotel["id"]
    hotel_link = f'https://www.hotels.com/ho{hotel_id}'

    hotel_description = f'Отель: {hotel_name}\n' \
                        f'Расположен по адресу: {country},\t{city},\t{street_adr}\n' \
                        f'Расстояние от центра (км): {distance}\n' \
                        f'Цена за ночь: {price_per_night} рублей\n' \
                        f'Общая стоимость: {total_price}\n рублей' \

    bot.send_message(chat_id, hotel_description,
                     reply_markup=hotel_details_keyboard(hotel_id, hotel_link, False, False))


@bot.callback_query_handler(func=lambda call: call.data.startswith('PHOTO'),
                            state=TravelInfoState.show_hotels)
def show_hotel_with_photo(callback: CallbackQuery) -> None:
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
