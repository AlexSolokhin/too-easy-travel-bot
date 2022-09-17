import json
import re
from typing import Dict, Optional
from . import connect_rapid_api
from loader import rapid_api


def request_location(location_group: str, location: str) -> Optional[Dict]:
    """
    Принимает на вход строку и возвращает словарь с ID наиболее близких к введённой строке локаций.
    Если возникли проблемы с подключением к API, возвращает сообщение об ошибке.

    :param location_group: группа, в которой ищем локацию
    :type location_group: str
    :param location: локация, указанная пользователем
    :type location: str
    :return: locations_id или None
    :rtype: Dict[str]
    """

    req_params = {"query": location, "locale": "ru_RU", "currency": "RUB"}
    response = connect_rapid_api('https://hotels4.p.rapidapi.com/locations/v2/search', rapid_api, req_params)

    if response:
        try:
            pattern = fr'(?<=\"{location_group}\",).+?[\]]'
            search_pattern = re.search(pattern, response.text)

            if search_pattern:
                resp_json = json.loads(f'{{{search_pattern[0]}}}')
                locations_dict = {}
                for location in resp_json['entities']:
                    locations_dict[location['name']] = location['destinationId']
                return locations_dict
            else:
                raise Exception
        except Exception as error:
            print(error)
            # TODO Добавить логирование сюда и передачу ошибки в бот

