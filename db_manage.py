import sqlite3


class DataBaseError(Exception):
    def __init__(self, text):
        self.text = text


def connect() -> sqlite3:
    connection = sqlite3.connect('hotel_bot.db')
    return connection


def update_line(query, field_value=None):
    try:
        connection = sqlite3.connect('hotel_bot.db')
        cursor = connection.cursor()
        cursor.execute(query, field_value)
        connection.commit()
        cursor.close()
        connection.close()
    except sqlite3.Error as err:
        print('При создании таблицы возникла ошибка:', err)
        return False


def get_line(query, field_value=None):
    try:
        connection = sqlite3.connect('hotel_bot.db')
        cursor = connection.cursor()
        cursor.execute(query, field_value)
        query_line = cursor.fetchone()
        cursor.close()
        connection.close()
        return query_line
    except sqlite3.Error as err:
        print('При запросе к таблице возникла ошибка:', err)
        return False


def get_all_lines(query, field_value=None):
    try:
        connection = sqlite3.connect('hotel_bot.db')
        cursor = connection.cursor()
        cursor.execute(query, field_value)
        query_line = cursor.fetchall()
        cursor.close()
        connection.close()
        return query_line
    except sqlite3.Error as err:
        print('При запросе к таблице возникла ошибка:', err)
        return False


def create_db_request():
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
