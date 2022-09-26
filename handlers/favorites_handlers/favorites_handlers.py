from loader import bot
from config_data.config import db
from datetime import datetime
from telebot.types import Message, CallbackQuery
from states.travel_information import TravelInfoState
from database.db_models import Favorites, Users
from database.favorites_db_methods import add_favorite_to_db, delete_favorite_from_db
from keyboards.inline_keyboards.hotel_details import hotel_details_keyboard

# TODO Добавить условие, если избранного нет


@bot.message_handler(commands=['favorites'])
def show_favorites(message: Message) -> None:
    """
    Показ избранных отелей.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    telegram_id = message.chat.id
    bot.set_state(message.from_user.id, TravelInfoState.show_favorites, message.chat.id)

    with db:
        favorite_hotels = Favorites.select().join(Users).where(Users.telegram_id == telegram_id)
        for hotel in favorite_hotels:
            hotel_id = hotel.hotel_id

            bot.send_message(message.chat.id, hotel.hotel,
                             reply_markup=hotel_details_keyboard(hotel_id, False, True))


@bot.callback_query_handler(func=lambda call: call.data.startswith('ADD_FAVORITE'))
def add_favorite(callback: CallbackQuery) -> None:
    """
    Добавление отеля в избранное.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """

    callback_data = callback.data.split('|')
    hotel_id = int(callback_data[1])
    hotel_descr = callback.message.text

    add_favorite_to_db(callback.message.chat.id, hotel_id, hotel_descr)
    bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id,
                                  reply_markup=hotel_details_keyboard(hotel_id, False, True))

    bot.answer_callback_query(callback.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('DELETE_FAVORITE'))
def delete_favorite(callback: CallbackQuery) -> None:
    """
    Исключение отеля из избранного.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """

    callback_data = callback.data.split('|')
    hotel_id = int(callback_data[1])

    delete_favorite_from_db(callback.message.chat.id, hotel_id)
    bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id,
                                  reply_markup=hotel_details_keyboard(hotel_id, False, False))

    bot.answer_callback_query(callback.id)
