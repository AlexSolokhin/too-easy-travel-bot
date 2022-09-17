import sqlite3
from typing import Any, Optional, Tuple, List


def connect():
    """
    Создаёт соединение с базой данных

    :return: connection
    :rtype: Connection
    """
    connection = sqlite3.connect('hotel_bot.db')
    return connection


def update_line(query: str, field_value: Optional[Tuple] = None):
    """
    Изменяет строку в базе данных

    :param query: sql-запрос к необходимой строке
    :param field_value: параметры для sql-запроса (если есть)
    """
    connection = sqlite3.connect('hotel_bot.db')
    cursor = connection.cursor()
    cursor.execute(query, field_value)
    connection.commit()
    cursor.close()
    connection.close()


def get_line(query: str, field_value: Optional[Tuple] = None) -> Tuple[Any]:
    """
    Возвращает строку из базы данных в соответствии с запросом

    :param query: sql-запрос к необходимой строке
    :param field_value: параметры для sql-запроса (если есть)
    :return: query_line
    :rtype: Tuple
    """
    connection = sqlite3.connect('hotel_bot.db')
    cursor = connection.cursor()
    cursor.execute(query, field_value)
    query_line = cursor.fetchone()
    cursor.close()
    connection.close()
    return query_line


def get_all_lines(query: str, field_value: Optional[Tuple] = None) -> List[Tuple]:
    """
    Возвращает все строки из базы данных в соответствии с запросом

    :param query: sql-запрос к необходимой строке
    :param field_value: параметры для sql-запроса (если есть)
    :return: query_lines
    :rtype: List[Tuple]
    """
    connection = sqlite3.connect('hotel_bot.db')
    cursor = connection.cursor()
    cursor.execute(query, field_value)
    query_lines = cursor.fetchall()
    cursor.close()
    connection.close()
    return query_lines


def create_db_request():
    """
    Создаёт базу данных для работы бота. Т.к. база данных уже создана не используется в приложении.
    Может быть удалена/скрыта или сохранена для возможного повторного создания БД.
    """
    connection = sqlite3.connect('hotel_bot.db')
    table_creation = '''CREATE TABLE user_requests (
                        `id` INTEGER PRIMARY KEY,
                        `date_time` DATETIME,
                        `command` TEXT,
                        `user_id` INTEGER,
                        `location` TEXT,
                        `check_in_date` DATETIME,
                        `check_out_date` DATETIME,
                        `hotel_num` INTEGER,
                        `need_photo` INT,
                        `photo_num` INT,
                        `min_price` REAL,
                        `max_price` REAL,
                        `min_dist` REAL,
                        `max_dist` REAL,
                        `result_id` INT);'''
    cursor = connection.cursor()
    cursor.execute(table_creation)
    connection.commit()
    cursor.close()
