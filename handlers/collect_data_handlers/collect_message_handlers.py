from loader import bot
from config_data.config import CALENDAR, CALENDAR_CALLBACK
from re import fullmatch
from telebot.types import Message
from states.travel_information import TravelInfoState
from handlers.API_handlers import request_location
from utils.restart_and_cancel import restart_search, cancel_search
from utils.summary_message import summary_message_handler
from keyboards.inline_keyboards.location_type import location_type_keyboard
from keyboards.inline_keyboards.specify_location import specify_location_keyboard
from keyboards.inline_keyboards.calendar import calendar_keyboard
from keyboards.reply_keyboards.default_keyboard import default_keyboard


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal'])
def start_search(message: Message) -> None:
    """
    Начало поиска: сохранение выбранной команды и запрос типа локации (город, вокзал, достопримечательность)

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if message.text == '/lowprice':
        first_message_text = 'Ищем самые дешёвые отели 🏢'
    elif message.text == '/highprice':
        first_message_text = 'Ищем самые дорогие отели 🏰'
    else:
        first_message_text = 'Ищем отели по твоему запросу 👁'

    bot.set_state(message.from_user.id, TravelInfoState.location_type, message.chat.id)

    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}✌!\n{first_message_text}\n\n'
                                      f'Где будем искать?',
                     reply_markup=location_type_keyboard())

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data.clear()
        data['command'] = message.text[1:]


@bot.message_handler(state=TravelInfoState.location_type)
def location_type_echo(message: Message) -> None:
    """
    Отправляет сообщение с просьбой выбрать тип локации из списка.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if not check_cancel_or_try_again(message):
        bot.send_message(message.chat.id, 'Просто выбери нужный вариант с помощью кнопки ☝')


@bot.message_handler(state=TravelInfoState.location)
def get_location(message: Message) -> None:
    """
    Сохранение локации. Если API вернул несколько локаций, запрос на уточнение, если только одну, переход к поиску.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if not check_cancel_or_try_again(message):

        if message.text.isdigit():
            bot.send_message(message.chat.id, 'Название города или места не может состоять только из цифр. '
                                              'Попробуй ещё раз!')
        else:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                locations_response = request_location(data['location_type'], message.text)

            if locations_response:
                response_length = len(locations_response)

                if response_length > 1:
                    bot.set_state(message.from_user.id, TravelInfoState.specify_location, message.chat.id)
                    bot.send_message(message.chat.id,
                                     'Вот, что я нашёл! Выбери вариант, который тебе больше всего подходит?',
                                     reply_markup=specify_location_keyboard(locations_response))

                elif response_length == 1:
                    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                        data['location'] = message.text
                        data['location_id'] = list(locations_response.values())[0]

                    bot.set_state(message.from_user.id, TravelInfoState.checkin_date, message.chat.id)
                    bot.send_message(message.chat.id,
                                     'Выбери дату, когда ты планируешь заселяться? 📅',
                                     reply_markup=calendar_keyboard(CALENDAR, CALENDAR_CALLBACK))

                else:
                    bot.send_message(message.chat.id,
                                     'К сожалению, по твоему запросу я ничего не нашёл 😔\n Хочешь попробовать ещё раз?',
                                     reply_markup=default_keyboard())
            else:
                    bot.send_message(message.chat.id,
                                     '😵 Упс, кажется что-то пошло не так! Попробуй повторить поиск.\n'
                                     'Если ошибка будет повторяться снова и снова, свяжись с моим автором '
                                     '- @Alex_Solokhin',
                                     reply_markup=default_keyboard())


@bot.message_handler(state=TravelInfoState.specify_location)
def specify_location_echo(message: Message) -> None:
    """
    Отправляет сообщение с просьбой выбрать локацию из списка.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if not check_cancel_or_try_again(message):
        bot.send_message(message.chat.id, 'Просто нажми на самый подходящий вариант ☝')


@bot.message_handler(state=TravelInfoState.checkin_date)
def specify_location_echo(message: Message) -> None:
    """
    Отправляет сообщение с просьбой выбрать дату заезда в календаре.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if not check_cancel_or_try_again(message):
        bot.send_message(message.chat.id, 'Просто выбери дату заезда в календаре ☝')


@bot.message_handler(state=TravelInfoState.checkout_date)
def specify_location_echo(message: Message) -> None:
    """
    Отправляет сообщение с просьбой дату выезда в календаре.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if not check_cancel_or_try_again(message):
        bot.send_message(message.chat.id, 'Просто выбери дату выезда в календаре ☝')


@bot.message_handler(state=TravelInfoState.min_price)
def get_min_price(message: Message) -> None:
    """
    Сохранение минимальную цену и запрашивает максимальную цену.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if not check_cancel_or_try_again(message):

        if message.text.isdigit():
            bot.set_state(message.from_user.id, TravelInfoState.max_price, message.chat.id)

            bot.send_message(message.chat.id, 'Какой твой верхний порог цены за ночь?')

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['min_price'] = int(message.text)
        else:
            bot.send_message(message.chat.id, 'Некорректно указана цена.\n '
                                              'Убедись, что в твоём сообщении только сумма без пробелов и символов и '
                                              'попробуй ещё раз!')


@bot.message_handler(state=TravelInfoState.max_price)
def get_max_price(message: Message) -> None:
    """
    Сохранение максимальную цену и запрашивает минимальное расстояние от центра.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if not check_cancel_or_try_again(message):

        if message.text.isdigit():

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                if int(message.text) > data['min_price']:
                    bot.set_state(message.from_user.id, TravelInfoState.min_dist, message.chat.id)
                    bot.send_message(message.chat.id, 'Какое минимальное расстояние (в км) от центра тебя бы устроило?'
                                                      '\nЕсли хочешь указать дробное значение, вводи его через точку, '
                                                      'без пробелов и других символов.')
                    data['max_price'] = int(message.text)

                else:
                    bot.send_message(message.chat.id, 'Максимальная цена должна быть больше минимальной цены.\n '
                                                      'Попробуй ещё раз!')

        else:
            bot.send_message(message.chat.id, 'Некорректно указана цена.\n '
                                              'Убедись, что в твоём сообщении только сумма без пробелов и символов и '
                                              'попробуй ещё раз!')


@bot.message_handler(state=TravelInfoState.min_dist)
def get_min_dist(message: Message) -> None:
    """
    Сохранение минимальное расстояние от центра и запрашивает максимальное расстояние от центра.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if not check_cancel_or_try_again(message):

        if fullmatch(r'^\d+\.?\d*$', message.text):

            bot.set_state(message.from_user.id, TravelInfoState.max_dist, message.chat.id)
            bot.send_message(message.chat.id, 'Какое максимальное расстояние (в км) от центра тебя бы устроило?\n'
                                              'Если хочешь указать дробное значение, вводи его через точку, '
                                              'без пробелов и других символов.')

            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['min_dist'] = float(message.text)

        else:
            bot.send_message(message.chat.id, 'Некорректно указано расстояние.\n '
                                              'Убедись, что ввёл число или дробное число через точку, не использовал '
                                              'пробелов и других символов и попробуй ещё раз!')


@bot.message_handler(state=TravelInfoState.max_dist)
def get_max_dist(message: Message) -> None:
    """
    Сохранение максимальное расстояние от центра и запрашивает максимальное расстояние от центра.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    if not check_cancel_or_try_again(message):

        if fullmatch(r'^\d+\.?\d*$', message.text):
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                if float(message.text) > data['min_dist']:
                    data['max_dist'] = float(message.text)
                    summary_message_handler(data, message.chat.id)
                    bot.set_state(message.from_user.id, TravelInfoState.show_hotels, message.chat.id)

                else:
                    bot.send_message(message.chat.id, 'Максимальное расстояние должно быть меньше '
                                                      'минимального расстояния.'
                                                      '\nПопробуй ещё раз!')
        else:
            bot.send_message(message.chat.id, 'Некорректно указано расстояние.\n '
                                              'Убедись, что ввёл число или дробное число через точку, не использовал '
                                              'пробелов и других символов и попробуй ещё раз!')


def check_cancel_or_try_again(message: Message) -> bool:
    """
    Вспомогательная функция. Вызывает функции отмены или перезапуска при вводе соответствующих сообщений.

    :param message: Объект сообщения.
    :type message: Message
    :return: bool
    """
    if message.text.lower() == '↩начать сначала':
        restart_search(message.from_user.id, message.chat.id)
        return True

    elif message.text.lower() == '🛑прервать поиск':
        cancel_search(message.from_user.id, message.chat.id)
        return True

    return False
