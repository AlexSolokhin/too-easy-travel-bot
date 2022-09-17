from loader import bot
from config_data.config import CALENDAR, CALENDAR_CALLBACK
from telebot.types import CallbackQuery
from datetime import datetime
from states.travel_information import TravelInfoState
from handlers.other_handlers.search_stop_or_try_again import try_again_search, cancel_search
from handlers.hotels_handlers.search_results_handlers import summary_message_handler
from keyboards.inline_keyboards.calendar import calendar_keyboard
from keyboards.reply_keyboards.default_keyboard import default_keyboard


@bot.callback_query_handler(func=lambda call: call.data not in ('TRY_AGAIN', 'CANCEL'),
                            state=TravelInfoState.location_type)
def get_location_type(callback: CallbackQuery) -> None:
    """
    Выбор и сохранения типа локации и запрос самой локации.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """

    # TODO Решить: убирать или не убирать инлайн клавиатуру на следующих шагах
    # bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id, reply_markup=None)

    if callback.data == 'TRANSPORT_GROUP':
        bot.send_message(callback.message.chat.id, 'Понял! Буду искать рядом с аэропортом или вокзалом.')
        bot.send_message(callback.message.chat.id, 'Теперь введи сам город и название аэропорта или вокзала?',
                         reply_markup=default_keyboard())

    elif callback.data == 'LANDMARK_GROUP':
        bot.send_message(callback.message.chat.id, 'Понял! Буду искать рядом с достопримечательностями.')
        bot.send_message(callback.message.chat.id, 'Теперь введи город и достопримечательность, '
                                                   'рядом с которой надо найти отель?',
                         reply_markup=default_keyboard())

    elif callback.data == 'CITY_GROUP':
        bot.send_message(callback.message.chat.id, 'Понял! Буду искать в городе без привязки к каким-то местам.')
        bot.send_message(callback.message.chat.id, 'Теперь введи город?', reply_markup=default_keyboard())

    bot.set_state(callback.from_user.id, TravelInfoState.location, callback.message.chat.id)

    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        data['location_type'] = callback.data

    bot.answer_callback_query(callback.id)


@bot.callback_query_handler(func=lambda call: call.data not in ('TRY_AGAIN', 'CANCEL'),
                            state=TravelInfoState.specify_location)
def get_specified_location(callback: CallbackQuery) -> None:
    """
    Выбор и сохранение уточнённой локации и запрос даты заезда в календаре.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """
    # TODO Настроить валидацию даты, если дата раньше, чем сегодня

    bot.set_state(callback.from_user.id, TravelInfoState.checkin_date, callback.message.chat.id)
    bot.send_message(callback.message.chat.id, 'Выбери дату, когда ты планируешь заселяться?',
                     reply_markup=calendar_keyboard(CALENDAR, CALENDAR_CALLBACK))

    with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
        location_list = callback.data.split('|')
        data['location'] = location_list[0]
        data['location_id'] = location_list[1]

    bot.answer_callback_query(callback.id)


@bot.callback_query_handler(func=lambda call: call.data not in ('TRY_AGAIN', 'CANCEL'),
                            state=TravelInfoState.checkin_date)
def get_checkin_date(callback: CallbackQuery) -> None:
    """
    Выбор и сохранение даты заезда и запрос даты выезда в календаре.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """

    name, action, year, month, day = callback.data.split(CALENDAR_CALLBACK.sep)
    date = CALENDAR.calendar_query_handler(bot=bot,
                                           call=callback,
                                           name=name,
                                           action=action,
                                           year=year,
                                           month=month,
                                           day=day)

    if action == 'DAY':

        if date < datetime.now():
            bot.send_message(callback.message.chat.id, 'Дата заезда не должна быть в прошлом. Попробуй ещё раз!',
                             reply_markup=calendar_keyboard(CALENDAR, CALENDAR_CALLBACK))

        bot.send_message(callback.message.chat.id, f'Выбрана дата заезда: {date.strftime("%d-%m-%Y")}')
        bot.set_state(callback.from_user.id, TravelInfoState.checkout_date, callback.message.chat.id)
        bot.send_message(callback.message.chat.id, 'Выбери дату, когда ты планируешь выселяться?',
                         reply_markup=calendar_keyboard(CALENDAR, CALENDAR_CALLBACK))

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            data['checkin_date'] = date

    elif action == 'CANCEL':
        cancel_search(callback.from_user.id, callback.message.chat.id)

    bot.answer_callback_query(callback.id)


@bot.callback_query_handler(func=lambda call: call.data not in ('TRY_AGAIN', 'CANCEL'),
                            state=TravelInfoState.checkout_date)
def get_checkout_date(callback: CallbackQuery) -> None:
    """
    Выбор и сохранение даты выезда. Запрос дополнительных фильтров или переход к выдаче.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """

    name, action, year, month, day = callback.data.split(CALENDAR_CALLBACK.sep)
    date = CALENDAR.calendar_query_handler(bot=bot,
                                           call=callback,
                                           name=name,
                                           action=action,
                                           year=year,
                                           month=month,
                                           day=day)

    if action == 'DAY':

        with bot.retrieve_data(callback.from_user.id, callback.message.chat.id) as data:
            if date <= data['checkin_date']:
                bot.send_message(callback.message.chat.id,
                                 'Дата выезда должна быть позже даты заезда. Попробуй ещё раз!',
                                 reply_markup=calendar_keyboard(CALENDAR, CALENDAR_CALLBACK))

            else:
                bot.send_message(callback.message.chat.id,
                                 f'Выбрана дата выезда: {date.strftime("%d-%m-%Y")}')

                data['checkout_date'] = date

                if data.get('command', None) == 'bestdeal':
                    bot.set_state(callback.from_user.id, TravelInfoState.min_price, callback.message.chat.id)
                    bot.send_message(callback.message.chat.id, 'Какой твой нижний порог цены за ночь?',
                                     reply_markup=default_keyboard())

                else:
                    summary_message_handler(data, callback.message.chat.id)
                    bot.set_state(callback.from_user.id, TravelInfoState.show_hotels, callback.message.chat.id)

    elif action == 'CANCEL':
        cancel_search(callback.from_user.id, callback.message.chat.id)

        bot.answer_callback_query(callback.id)


@bot.callback_query_handler(func=lambda call: call.data == 'TRY_AGAIN')
def try_again_callback_handler(callback: CallbackQuery) -> None:
    """
    Вызов команды перезапуска поиска из коллбэка.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """
    bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id, reply_markup=None)
    try_again_search(callback.from_user.id, callback.message.chat.id)
    bot.answer_callback_query(callback.id)


@bot.callback_query_handler(func=lambda call: call.data == 'CANCEL')
def cancel_callback_handler(callback: CallbackQuery) -> None:
    """
    Вызов команды остановки поиска из коллбэка.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """
    bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id, reply_markup=None)
    cancel_search(callback.from_user.id, callback.message.chat.id)
    bot.answer_callback_query(callback.id)
