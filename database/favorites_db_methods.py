from config_data.config import db
from database.db_models import Users, Favorites
from logger_config import logger


@logger.catch
def add_favorite_to_db(telegram_id: int, hotel_id: int, hotel_descr: str) -> None:
    """
    Добавление избранного отеля в базу данных

    :param telegram_id: id пользователя в телеграмме
    :type telegram_id: int
    :param hotel_id: id отеля
    :type hotel_id: int
    :param hotel_descr: Описание отеля
    :type hotel_descr: str
    :return: None
    """

    with db:
        user, created = Users.get_or_create(telegram_id=telegram_id)
        Favorites.get_or_create(user=user, hotel_id=hotel_id, hotel=hotel_descr)


@logger.catch
def delete_favorite_from_db(telegram_id: int, hotel_id: int) -> None:
    """
    Удаляет отель из избранного.

    :param telegram_id: id пользователя в телеграмме
    :type telegram_id: int
    :param hotel_id: id отеля
    :type hotel_id: int
    :return: None
    """

    with db:
        favorite = Favorites\
            .select()\
            .join(Users)\
            .where(Users.telegram_id == telegram_id, Favorites.hotel_id == hotel_id)\
            .get()

        favorite.delete_instance()
