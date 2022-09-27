import json
import re
import datetime
from typing import List, Optional
from . import connect_rapid_api
from loader import rapid_api
from logger_config import logger


@logger.catch
def request_hotels(search_data: dict, page: int = 1) -> Optional[List]:
    """
    Принимает на вход словарь с ответами пользователя, дополнительно его обрабатывает.
    Возвращает словарь с отелями, которые удовлетворяют условиям поиска.
    Если возникли проблемы с подключением к API, возвращает сообщение об ошибке.

    :param search_data: словарь с ответами пользователя.
    :type search_data: dict
    :param page: номер возвращаемой страницы
    :type page: int
    :return: список отелей или None
    :rtype: List
    """

    command = search_data.get('command', None)
    if command == 'highprice':
        sort_order = 'PRICE_HIGHEST_FIRST'
    else:
        sort_order = 'PRICE'

    checkin_date = search_data['checkin_date']
    checkout_date = search_data['checkout_date']

    req_params = {
        "destinationId": search_data.get('location_id', None),
        "checkIn": datetime.datetime.strftime(checkin_date, '%Y-%m-%d'),
        "checkOut": datetime.datetime.strftime(checkout_date, '%Y-%m-%d'),
        "sortOrder": sort_order,
        "priceMin": search_data.get('min_price', None),
        "priceMax": search_data.get('max_price', None),
        "pageNumber": str(page),
        "pageSize": "25",
        "adults1": "1",
        "locale": "ru_RUS",
        "currency": "RUB"
    }
    response = connect_rapid_api('https://hotels4.p.rapidapi.com/properties/list', rapid_api, req_params)

    if response:
        resp_json = json.loads(response.text)
        results = resp_json.get('data', None).get('body', None).get('searchResults', None).get('results', None)

        hotels_list = []
        min_dist = search_data.get('min_dist', -1)
        max_dist = search_data.get('max_dist', -1)

        for hotel in results:
            from_center = 'n/d'

            for landmark in hotel['landmarks']:
                if landmark.get('label', None) == 'City center':
                    # Получаю расстояние до центра, убираю лишнее, перевожу во float, и перевожу из миль в км
                    from_center = round(float(re.sub(r'[^\d.]', '', landmark['distance'])) * 1.609, 1)

            if command == 'bestdeal' and (from_center == 'n/d' or from_center < min_dist or from_center > max_dist):
                continue

            price = hotel['ratePlan']['price'].get('exactCurrent', 'n/d')

            if not isinstance(price, str):
                total_price = price * (checkout_date - checkin_date).days
            else:
                total_price = 'n/d'

            new_hotel = {
                'id': hotel['id'],
                'name': hotel['name'],
                'address': hotel['address'],
                'from_center': from_center,
                'price': round(price, 2),
                'total_price': round(total_price, 2)
            }

            hotels_list.append(new_hotel)

        return hotels_list
