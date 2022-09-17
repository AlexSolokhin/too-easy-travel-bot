import json
import re
from typing import List, Optional
from . import connect_rapid_api
from loader import rapid_api


def request_photo(hotel_id: int) -> Optional[List]:

    req_params = {"id": hotel_id}
    response = connect_rapid_api('https://hotels4.p.rapidapi.com/properties/get-hotel-photos', rapid_api, req_params)

    if response:
        resp_json = json.loads(response.text)

        hotel_images = resp_json['hotelImages']
        hotel_images_length = len(hotel_images)

        photos_links = []

        for elem in range(0, 10):
            # Хардкодом ограничиваю количество фото до 10
            if elem > hotel_images_length:
                break

            base_url = hotel_images[elem]['baseUrl']
            photo_url = re.sub(r'{size}', 'y', base_url)
            photos_links.append(photo_url)
            elem += 1

        return photos_links
