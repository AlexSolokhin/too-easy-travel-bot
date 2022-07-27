import json
import requests
from datetime import datetime
from re import sub
from typing import Dict, List


class HotelAPIHandler:
    """
    Базовый класс для работы с API. Принимает детали запроса пользователя.

    Args:
        check-in (datetime): дата заезда
        check-out (datetime): дата выезда
        result_limit (int): количество отелей в выдаче
        need_photo (int): необходимость в фото (0 - нет, 1 - да)
        photo_limit (int): количество фото для каждого отеля в выдаче
        min_price (str): минимальная цена
        max_price (str): максимальная цена
        sorting (str): порядок сортировки (зависит от команды)
        min_dist (float): минимальное допустимое расстояние от центра
        max_dist (float): максимальное допустимое расстояние от центра
        adults (str): количество взрослых гостей (1 по умолчанию)
    """
    def __init__(self, check_in: datetime, check_out: datetime, result_limit: int, need_photo: int, photo_limit: int,
                 min_price: str, max_price: str, sorting: str, min_dist: float, max_dist: float, adults: str = '1'):
        self.__headers = {"X-RapidAPI-Key": "b845314e6amsh1ff806ffbc19bdap1bff38jsnb706e99b12b0",
                          "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
        self.__check_in = check_in
        self.__check_out = check_out
        self.__result_limit = result_limit
        self.__photo_limit = photo_limit
        self.__need_photo = need_photo
        self.__min_price = min_price
        self.__max_price = max_price
        self.__min_dist = min_dist
        self.__max_dist = max_dist
        self.__sorting = sorting
        self.__adults = adults

    @property
    def headers(self) -> Dict:
        """
        Геттер для получения хэдера запроса (содержит токен)

        :return: __headers
        :rtype: Dict
        """
        return self.__headers

    @property
    def check_in(self) -> datetime:
        """
        Геттер для получения даты заезда

        :return: __check_in
        :rtype: datetime
        """
        return self.__check_in

    @property
    def check_out(self) -> datetime:
        """
        Геттер для получения даты выезда

        :return: __check_out
        :rtype: datetime
        """
        return self.__check_out

    @property
    def result_limit(self) -> int:
        """
        Геттер для максимального количества отелей в выдаче

        :return: __result_limit
        :rtype: int
        """
        return self.__result_limit

    @property
    def photo_limit(self) -> int:
        """
        Геттер для максимального количества фото на один отель в выдаче

        :return: __photo_limit
        :rtype: int
        """
        return self.__photo_limit

    @property
    def need_photo(self) -> int:
        """
        Геттер для значения необходимости в фото

        :return: __need_photo
        :rtype: int
        """
        return self.__need_photo

    @property
    def min_price(self) -> str:
        """
        Геттер для минимальной цены за ночь

        :return: __min_price
        :rtype: str
        """
        return self.__min_price

    @property
    def max_price(self) -> str:
        """
        Геттер для максимальной цены за ночь

        :return: __max_price
        :rtype: str
        """
        return self.__max_price

    @property
    def min_dist(self) -> float:
        """
        Геттер для минимальной дистанции до центра

        :return: __min_dist
        :rtype: float
        """
        return self.__min_dist

    @property
    def max_dist(self) -> float:
        """
        Геттер для максимальной дистанции до центра

        :return: __max_dist
        :rtype: float
        """
        return self.__max_dist

    @property
    def sorting(self) -> str:
        """
        Геттер для параметра сортировки результатов

        :return: __sorting
        :rtype: str
        """
        return self.__sorting

    @property
    def adults(self) -> str:
        """
        Геттер для количества взрослых гостей

        :return: __adults
        :rtype: str
        """
        return self.__adults

    def find_location(self, location: str) -> Dict:
        """
        Принимает на вход строку и возвращает словарь с ID наиболее близких к введнной строке локаций

        :param location: локация, указанная пользователем
        :return: locations_id
        :rtype: Dict
        """
        req_params = {"query": location, "locale": "ru_RU", "currency": "RUB"}
        response = requests.get('https://hotels4.p.rapidapi.com/locations/v2/search',
                                headers=self.headers,
                                params=req_params)
        resp_json = json.loads(response.text)
        locations_id = {}
        for location_group in resp_json['suggestions']:
            for location in location_group['entities']:
                locations_id[location['name']] = location['destinationId']
        return locations_id

    def find_hotels(self, location_ids: Dict) -> Dict:
        """
        Запрашивает отели в локациях из location_ids, возвращает словарь с отелями и их параметрами

        :param location_ids: словарь с ID локаций
        :return: hotels_dict
        :rtype: Dict
        """
        hotels_dict = {}
        hotels_count = 0
        for location in location_ids.values():
            req_params = {"destinationId": location,
                          "pageNumber": "1",
                          "pageSize": "100",
                          "checkIn": datetime.strftime(self.check_in, '%Y-%m-%d'),
                          "checkOut": datetime.strftime(self.check_out, '%Y-%m-%d'),
                          "adults1": self.adults,
                          "priceMin": self.min_price,
                          "priceMax": self.max_price,
                          "sortOrder": self.sorting,
                          "locale": "ru_RUS",
                          "currency": "RUB"}
            response = requests.get('https://hotels4.p.rapidapi.com/properties/list',
                                    headers=self.headers,
                                    params=req_params)
            resp_json = json.loads(response.text)

            if not resp_json.get('data', False):
                return hotels_dict

            for hotel in resp_json['data']['body']['searchResults']['results']:
                from_center = 'n/d'
                for landmark in hotel['landmarks']:
                    if landmark.get('label') == 'City center':
                        # Получаю расстояние до центра, убираю лишнее, перевожу во float, и перевожу из миль в км
                        from_center = round(float(sub(r'[^\d.]', '', landmark['distance'])) * 1.609, 1)

                if from_center == 'n/d' or self.min_dist >= from_center or from_center >= self.max_dist:
                    continue

                hotels_dict[hotels_count] = {
                    'id': hotel['id'],
                    'name': hotel['name'],
                    'address': hotel['address'],
                    'from_center': from_center,
                    'price': hotel['ratePlan']['price']['current']
                }

                if self.need_photo == 1:
                    hotels_dict[hotels_count]['photo'] = self.request_photo(hotel['id'])

                hotels_count += 1

                if hotels_count == self.result_limit:
                    break

            return hotels_dict

    def request_photo(self, hotel_id: str) -> List:
        """
        Запрашивает фото отеля по ID

        :param hotel_id: id отеля
        :return: photos_links
        :rtype: List
        """
        req_params = {"id": hotel_id}
        response = requests.get('https://hotels4.p.rapidapi.com/properties/get-hotel-photos',
                                headers=self.headers,
                                params=req_params)
        resp_json = json.loads(response.text)
        photos_links = []

        elem = 0
        for _ in range(self.photo_limit):
            if elem > len(resp_json['hotelImages']):
                break

            base_url = resp_json['hotelImages'][elem]['baseUrl']
            photo_url = sub(r'{size}', 'y', base_url)
            photos_links.append(photo_url)
            elem += 1

        return photos_links
