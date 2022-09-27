from loader import bot
from states.travel_information import TravelInfoState
from keyboards.inline_keyboards.location_type import location_type_keyboard


def restart_search(user_id: int, chat_id: int) -> None:
    """
    Перезапуск поиска с прежней командой.

    :param user_id: id пользователя
    :type user_id: int
    :param chat_id: id чата
    :type chat_id: int
    :return: None
    """

    bot.send_message(chat_id, 'Поиск перезапущен 👍')
    bot.send_message(chat_id, 'Где будем искать отели?', reply_markup=location_type_keyboard())

    bot.set_state(user_id, TravelInfoState.location_type, chat_id)

    with bot.retrieve_data(user_id, chat_id) as data:
        command = data['command']
        data.clear()
        data['command'] = command


def cancel_search(user_id: int, chat_id: int) -> None:
    """
    остановка поиска.

    :param user_id: id пользователя
    :type user_id: int
    :param chat_id: id чата
    :type chat_id: int
    :return: None
    """

    bot.send_message(chat_id, 'Поиск прерван 👍\nЕсли хочешь начать сначала введи команду или нажми /help')

    bot.set_state(user_id, None, chat_id)

    with bot.retrieve_data(user_id, chat_id) as data:
        data.clear()
