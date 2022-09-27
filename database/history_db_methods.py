from config_data.config import db
import json
import re
from database.db_models import Users, History
from logger_config import logger


@logger.catch
def add_history_to_db(telegram_id: int,
                      command: str,
                      location: str,
                      check_in: str,
                      check_out: str,
                      min_price: int,
                      max_price: int,
                      min_dist: float,
                      max_dist: float) -> None:
    """
    Создаём запись для истории поиска. Т.к. отели выдаются по одному, их подтягиваем позднее.

    :param telegram_id: id пользователя в телеграмме
    :type telegram_id: int
    :param command: команда пользователя
    :type command: str
    :param location: локация, которую ищет пользователь
    :type location: str
    :param check_in: дата заезда
    :type check_in: str
    :param check_out: дата выезда
    :type check_out: str
    :param min_price: минимальная цена
    :type max_price: int
    :param max_price: максимальная цена
    :type max_price: int
    :param min_dist: минимальная дистанция от центра
    :type min_dist: float
    :param max_dist: максимальная дистанция от центра
    :type max_dist: float

    :return: None
    """

    with db:

        user, created = Users.get_or_create(telegram_id=telegram_id)

        history_row = History(
            user=user,
            command=command,
            location=location,
            checkin_date=check_in,
            checkout_date=check_out,
            min_price=min_price,
            max_price=max_price,
            min_dist=min_dist,
            max_dist=max_dist,
            hotels='{}'
        )
        history_row.save()


@logger.catch
def add_hotels_to_history_db(telegram_id: int, hotel_id: int, hotel_name: str) -> None:
    """
    Добавляет отель в запись истории.

    :param telegram_id: id пользователя в телеграмме
    :type telegram_id: int
    :param hotel_id: id отеля
    :type hotel_id: int
    :param hotel_name: название отеля
    :type hotel_name: str

    :return: None
    """

    with db:
        hotel_link = f'https://www.hotels.com/ho{hotel_id}'

        history_row = History\
            .select()\
            .join(Users)\
            .where(Users.telegram_id == telegram_id)\
            .order_by(History.search_date.desc(), History.search_time.desc())\
            .get()

        hotels_dict = json.loads(history_row.hotels)
        hotels_dict[hotel_name] = hotel_link
        hotels_json = json.dumps(hotels_dict)

        history_row.hotels = hotels_json
        history_row.save()


def history_row_to_message(record: History) -> str:
    """
    Обрабатывает строку в базе данных и возвращает сообщение для пользователя.

    :param record: одна запись истории - объект модели History
    :type record: History
    :return: Сообщение для пользователя (адаптировано под MarckupV2)
    :rtype: int
    """

    search_date = record.search_date.strftime("%d-%m-%Y")
    search_time = record.search_time.strftime("%H:%M")
    command = record.command
    location = record.location
    check_in = record.checkin_date
    check_out = record.checkout_date
    min_price = record.min_price
    max_price = record.max_price
    min_dist = record.min_dist
    max_dist = record.max_dist
    hotels = record.hotels

    base_message = f'{search_date} {search_time}\n*Команда:* {command}, *локация:* {location}\n' \
                   f'*Дата заезда:* {check_in}, *дата выезда:* {check_out}\n'

    message_extender = ''
    if command == 'bestdeal':
        message_extender = f'*Минимальная цена:* {min_price}, *максимальная цена*: {max_price}\n' \
                           f'*Минимальное расстояние до центра:* {min_dist}\n' \
                           f'*Максимальное расстояние до центра:* {max_dist}\n'

    extended_message = base_message + message_extender

    extended_message = re.sub(r'[(]', r'[\(]', extended_message)
    extended_message = re.sub(r'[)]', r'[\)]', extended_message)
    extended_message = re.sub(r'[.]', r'[\.]', extended_message)

    hotels_dict = json.loads(hotels)
    hotels_message = '\n*Показанные отели:*'
    for hotel in hotels_dict.items():
        hotel_name = hotel[0]
        hotel_name = re.sub(r'[.]', r'[\.]', hotel_name)
        hotel_name = re.sub(r'[(]', r'[\(]', hotel_name)
        hotel_name = re.sub(r'[)]', r'[\)]', hotel_name)

        hotel_link = hotel[1]
        hotel_string = f'\n[{hotel_name}]({hotel_link})'
        hotels_message += hotel_string

    history_message = extended_message + hotels_message

    history_message = re.sub(r'-', r'[\-]', history_message)

    return history_message
