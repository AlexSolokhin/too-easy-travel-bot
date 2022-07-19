import json
import requests
from datetime import datetime
from re import sub
from typing import Dict, List, Union


class HotelAPIHandler:
    def __init__(self, check_in, check_out, result_limit, need_photo, photo_limit,
                 min_price, max_price, sorting, min_dist, max_dist, adults='1'):
        self.headers = {"X-RapidAPI-Key": "b845314e6amsh1ff806ffbc19bdap1bff38jsnb706e99b12b0",
                        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}
        self.check_in = check_in
        self.check_out = check_out
        self.result_limit = result_limit
        self.photo_limit = photo_limit
        self.need_photo = need_photo
        self.min_price = min_price
        self.max_price = max_price
        self.min_dist = min_dist
        self.max_dist = max_dist
        self.sorting = sorting
        self.adults = adults

    def find_location(self, location: str) -> Dict:
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

    def find_hotels(self, location_ids: Dict) -> Union[Dict, str]:
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
                return 'Извини, но я не нашёл отелей, соответствующих условиям поиска :('

            for hotel in resp_json['data']['body']['searchResults']['results']:
                from_center = 'n/d'
                for landmark in hotel['landmarks']:
                    if landmark.get('label') == 'City center':
                        # Получаю расстояние до центра, убираю лишнее, перевожу во float, и перевожу из миль в км
                        from_center = float(sub(r'[^\d.]', '', landmark['distance'])) * 1.609

                if self.min_dist and \
                        (from_center == 'n/d' or (self.min_dist >= from_center or from_center >= self.max_dist)):
                    continue

                hotels_dict[hotels_count] = {
                    'id': hotel['id'],
                    'name': hotel['name'],
                    'address': hotel['address'],
                    'from_center': round(from_center, 2),
                    'price': hotel['ratePlan']['price']['current']
                }

                if self.need_photo == 1:
                    hotels_dict[hotels_count]['photo'] = self.request_photo(hotel['id'])

                hotels_count += 1

                if hotels_count == self.result_limit:
                    break

            return hotels_dict

    def request_photo(self, hotel_id: str) -> List:
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
