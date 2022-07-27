import re
import db_manage
import keybords
import telebot
from Hotel_API import HotelAPIHandler
from datetime import datetime
from re import fullmatch
from typing import Dict


class Dialog:
    """
    Базовый класс диалога. Содержит цепочку методов для сбора данных от пользователя и обработки результатов запроса.
    Диалог запускается при вызове экземпляра.

    Args:
        message (Message): объект сообщения
        max_hotel (int): максимальное количество отелей, которое может показать бот. 10 по умолчанию.
        max_photo (int): максимальное количество фото одного отеля, которое может показать бот. 10 по умолчанию.
    """
    def __init__(self,  message, max_hotel: int = 10, max_photo: int = 10):
        self.__command = message.text
        self.__user_id = message.from_user.id
        self.__chat = message.chat.id
        self.__max_hotel = max_hotel
        self.__max_photo = max_photo

    def __call__(self, message, bot: telebot, *args, **kwargs):
        answers = {}
        self.ask_location(message, bot, answers, 'Куда ты хочешь отправиться?')

    @property
    def command(self) -> str:
        """
        Геттер для получения команды

        :return: __command
        :rtype: str
        """
        return self.__command

    @property
    def user_id(self) -> int:
        """
        Геттер для получения id пользователя в ТГ

        :return: __user_id
        :rtype: int
        """
        return self.__user_id

    @property
    def chat(self) -> Dict:
        """
        Геттер для получения чата, в котором вызвали бота

        :return: __chat
        :rtype: Dict
        """
        return self.__chat

    @property
    def max_hotel(self) -> int:
        """
        Геттер для получения максимального количества отелей, которое может выдать бот

        :return: __max_hotel
        :rtype: int
        """
        return self.__max_hotel

    @property
    def max_photo(self) -> int:
        """
        Геттер для получения максимального количества фото, которое может выдать бот

        :return: __max_photo
        :rtype: int
        """
        return self.__max_photo

    def ask_location(self, message, bot: telebot, answers: Dict, text: str):
        """
        Запрашивает локацию для поиска отелей

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        :param text: текст запроса
        """
        bot.send_message(self.chat, text, reply_markup=keybords.simple_keyboard())
        bot.register_next_step_handler(message, self.check_location, bot, answers)

    def check_location(self, message, bot: telebot, answers: Dict):
        """
        Сохраняет введённую пользователем локацию и продолжает цепочку диалога

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        """
        if not self.stop_dialog(message, bot):
            answers['location'] = message.text
            self.ask_dates(message, bot, answers, 'Введи даты заезда и выезда в формате ДД-ММ-ГГГ '
                                                  'и раздели их одним пробелом.')

    def ask_dates(self, message, bot: telebot, answers: Dict, text: str):
        """
        Запрашивает даты поездки для поиска отелей

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        :param text: текст запроса
        """
        bot.send_message(self.chat, text, reply_markup=keybords.simple_keyboard())
        bot.register_next_step_handler(message, self.check_dates, bot, answers)

    def check_dates(self, message, bot: telebot, answers: Dict):
        """
        Проверяет корректность ввода дат поездки, сохраняет их и продолжает цепочку диалога

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)

        :raise IndexError: если пользователь ввёл не две даты
        :raise NameError: если дата заезда позже даты отъезда
        :raise RuntimeError: если дата заезда в прошлом
        """
        if not self.stop_dialog(message, bot):
            try:
                dates_list = message.text.split(' ')
                if len(dates_list) != 2:
                    raise IndexError('Нужно ввести две даты через один пробел.')
                checkin_date = datetime.strptime(dates_list[0], '%d-%m-%Y')
                checkout_date = datetime.strptime(dates_list[1], '%d-%m-%Y')
                if checkout_date <= checkin_date:
                    raise NameError('Дата отъезда меньше даты заезда. Попробуй ещё раз!')
                if checkin_date < datetime.now():
                    raise RuntimeError('Выбранная дата заезда находится в прошлом. Попробуй ещё раз!')
                answers['check-in'] = checkin_date
                answers['check-out'] = checkout_date
                self.ask_hotel_num(message, bot, answers, 'Я могу показать до {} отелей. '
                                                          'Сколько отелей максимально тебе показать?'
                                   .format(self.max_hotel))
            except ValueError:
                self.ask_dates(message, bot, answers, 'Неверный формат даты :(\n'
                                                      'Убедись, что даты соответствуют формату "ДД-ММ-ГГГГ" '
                                                      'и попробуй ещё раз')
            except (NameError, RuntimeError, IndexError) as error:
                self.ask_dates(message, bot, answers, error)

    def ask_hotel_num(self, message, bot: telebot, answers: Dict, text: str):
        """
        Запрашивает количество отелей, которое необходимо показать (не больше максимального)

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        :param text: текст запроса
        """
        bot.send_message(self.chat, text, reply_markup=keybords.one_to_ten_keyboard())
        bot.register_next_step_handler(message, self.check_hotel_num, bot, answers)

    def check_hotel_num(self, message, bot: telebot, answers: Dict):
        """
        Проверяет корректность ввода количества отелей, сохраняет его и продолжает цепочку диалога

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        """
        if not self.stop_dialog(message, bot):
            if not message.text.isdigit() or (self.max_hotel < int(message.text) or int(message.text) <= 0):
                self.ask_hotel_num(message, bot, answers,
                                   'Пожалуйста, напиши, сколько максимально тебе показать отелей '
                                   'от 1 до {} или прерви поиск'
                                   .format(self.max_hotel))
            else:
                answers['hotel_num'] = int(message.text)
                self.ask_need_photo(message, bot, answers, 'Показать фото отеля?')

    def ask_need_photo(self, message, bot: telebot, answers: Dict, text: str):
        """
        Запрашивает, нужно ли показать фото отелей

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        :param text: текст запроса
        """
        bot.send_message(self.chat, text, reply_markup=keybords.yes_no_keyboard())
        bot.register_next_step_handler(message, self.check_need_photo, bot, answers)

    def check_need_photo(self, message, bot: telebot, answers: Dict):
        """
        Проверяет корректность ввода необходимости фото, сохраняет его и продолжает цепочку диалога

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        """
        if not self.stop_dialog(message, bot):
            if message.text.lower() != 'да' and message.text.lower() != 'нет':
                self.ask_need_photo(message, bot, answers, 'Пожалуйста, напиши нужны ли тебе фото (да или нет) '
                                                           'или прерви поиск!')
            else:
                if message.text.lower() == 'да':
                    answers['need_photo'] = 1
                    self.ask_photo_num(message, bot, answers, 'Я могу показать до {} фотографий на 1 отель. '
                                                              'Сколько фото тебе показать?'.format(self.max_photo))
                else:
                    answers['need_photo'] = 0
                    if self.command == '/bestdeal':
                        self.ask_price_limit(message, bot, answers, 'Укажи через "-" минимальную и максимальную цену '
                                                                    'за ночь в рублях, которая тебя бы устроила?')
                    else:
                        self.proceed_result(bot, answers, 'Спасибо! Начинаю обрабатывать твой запрос!')

    def ask_photo_num(self, message, bot: telebot, answers: Dict, text: str):
        """
        Запрашивает количество фото для каждого отеля, которые нужно показать (не больше максимального)

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        :param text: текст запроса
        """
        bot.send_message(self.chat, text, reply_markup=keybords.one_to_ten_keyboard())
        bot.register_next_step_handler(message, self.check_photo_num, bot, answers)

    def check_photo_num(self, message, bot: telebot, answers: Dict):
        """
        Проверяет корректность ввода количества фото, сохраняет его и продолжает цепочку диалога

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        """
        if not self.stop_dialog(message, bot):
            if not message.text.isdigit() or (self.max_photo < int(message.text) or int(message.text) < 0):
                self.ask_photo_num(message, bot, answers,
                                   'Пожалуйста, напиши, сколько тебе показать фото от 1 до {} или прерви поиск'
                                   .format(self.max_photo))
            else:
                answers['photo_num'] = int(message.text)
                if self.command == '/bestdeal':
                    self.ask_price_limit(message, bot, answers, 'Укажи через "-" минимальную и максимальную '
                                                                'цену за ночь в рублях, которая тебя бы устроила?')
                else:
                    self.proceed_result(bot, answers, 'Спасибо! Начинаю обрабатывать твой запрос!')

    def ask_price_limit(self, message, bot: telebot, answers: Dict, text: str):
        """
        Запрашивает диапазон цен для поиска отелей

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        :param text: текст запроса
        """
        bot.send_message(self.chat, text, reply_markup=keybords.simple_keyboard())
        bot.register_next_step_handler(message, self.check_price_limit, bot, answers)

    def check_price_limit(self, message, bot: telebot, answers: Dict):
        """
        Проверяет корректность ввода диапазона цен, сохраняет его и продолжает цепочку диалога

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        """
        if not self.stop_dialog(message, bot):
            if not fullmatch(r'\d+\.?\d*\s?-\s?\d+\.?\d*', message.text) or \
                    float(''.join(message.text.split('-')[0].split())) > \
                    float(''.join(message.text.split('-')[1].split())):
                self.ask_price_limit(message, bot, answers,
                                     'Неверный формат сообщения :(\n'
                                     'Пожалуйста, укажи через "-" минимальную и максимальную цену '
                                     'за ночь в рублях?\n'
                                     'Убедись, что первое значение меньше второго.')
            else:
                min_price = ''.join(message.text.split('-')[0].split())
                max_price = ''.join(message.text.split('-')[1].split())
                answers['min_price'] = min_price
                answers['max_price'] = max_price
                self.ask_dist_limit(message, bot, answers,
                                    'Укажи через "-" минимальное и максимальное расстояние от центра в км, '
                                    'которое тебя бы устроило?')

    def ask_dist_limit(self, message, bot: telebot, answers: Dict, text: str):
        """
        Запрашивает диапозон дистанции для поиска отелей поиска отелей

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        :param text: текст запроса
        """
        bot.send_message(self.chat, text, reply_markup=keybords.simple_keyboard())
        bot.register_next_step_handler(message, self.check_dist_limit, bot, answers)

    def check_dist_limit(self, message, bot: telebot, answers: Dict):
        """
        Проверяет корректность ввода диапазона дистанции от центра, сохраняет его и продолжает цепочку диалога

        :param message: объект сообщения
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        """
        if not self.stop_dialog(message, bot):
            if not fullmatch(r'\d+\.?\d*\s?-\s?\d+\.?\d*', message.text) or \
                    float(''.join(message.text.split('-')[0].split())) > \
                    float(''.join(message.text.split('-')[1].split())):
                self.ask_dist_limit(message, bot, answers,
                                    'Неверный формат сообщения :(\n'
                                    'Пожалуйста, укажи минимальное и максимальное расстояние от центра, '
                                    'которое тебя бы устроило?\n'
                                    'Введи диапазон в км. через "-", дробные значения разделяй точкой.\n'
                                    'Убедись, что первое значение меньше второго.')
            else:
                min_dist = float(''.join(message.text.split('-')[0].split()))
                max_dist = float(''.join(message.text.split('-')[1].split()))
                answers['min_dist'] = min_dist
                answers['max_dist'] = max_dist
                self.proceed_result(bot, answers, 'Спасибо! Начинаю обрабатывать твой запрос!')

    def proceed_result(self, bot, answers: Dict, text: str):
        """
        Обрабатывает данные от пользователя (answers) и передаёт ответ от API далее по цепочке

        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        :param text: текст сообщения о начале обработки запроса
        """
        bot.send_message(self.chat, text)

        if self.command == '/highprice':
            sorting = 'PRICE_HIGHEST_FIRST'
        else:
            sorting = 'PRICE'

        searching_obj = HotelAPIHandler(answers.get('check-in'), answers.get('check-out'),
                                        answers.get('hotel_num'), answers.get('need_photo'),
                                        answers.get('photo_num'), answers.get('min_price', '0'),
                                        answers.get('max_price', '10000000'), sorting,
                                        answers.get('min_dist', 0), answers.get('max_dist', 100))

        hotels_returned = searching_obj.find_hotels((searching_obj.find_location(answers['location'])))
        self.send_result(hotels_returned, bot, answers)

    def send_result(self, hotels_returned: Dict, bot: telebot, answers: Dict):
        """
        Преобразует ответ от PI в человеко-читаемый вид и отправляет пользователю

        :param hotels_returned: словарь с отелями, которые удовлетворяют запросу
        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя (передается дальше по цепочке)
        """
        if len(hotels_returned) == 0:
            bot.send_message(self.chat, 'Извини, но я не нашёл отелей, соответствующих условиям поиска :(')
            hotel_string = 'Ни одного отеля не найдено :('
        else:
            full_days = (answers.get('check-out') - answers.get('check-in')).days

            hotels_list = []

            for hotels_num in range(0, max(len(hotels_returned), answers.get('hotel_num'))):
                # В регулярном выражении убираем все символы кроме цифр и точки, чтобы преобразовать цену к float
                price_per_night = float(re.sub(r'[^\d.]', '', hotels_returned[hotels_num]['price']))

                hotel_description = 'Отель: {hotel_name}\n' \
                                    'Расположен по адресу: {country},\t{city},\t{street_adr}\n' \
                                    'Расстояние от центра (км): {distance}\n' \
                                    'Цена за ночь (руб): {price_per_night}\n' \
                                    'Общая стоимость (руб): {total_price}\n' \
                                    'Ссылка на отель: https://www.hotels.com/ho{hotel_id}\n'\
                    .format(hotel_name=hotels_returned[hotels_num]['name'],
                            country=hotels_returned[hotels_num]['address']['countryName'],
                            city=hotels_returned[hotels_num]['address']['locality'],
                            street_adr=hotels_returned[hotels_num]['address']
                            .get('streetAddress', 'Полный адрес доступен после бронирования.'),
                            distance=hotels_returned[hotels_num]['from_center'],
                            price_per_night=price_per_night,
                            total_price=price_per_night * full_days,
                            hotel_id=hotels_returned[hotels_num]['id'])

                hotels_list.append(hotels_returned[hotels_num]['name'])

                bot.send_message(self.chat, hotel_description)
                if hotels_returned[hotels_num].get('photo', None):
                    for photo_url in hotels_returned[hotels_num]['photo']:
                        bot.send_photo(self.chat, photo_url)

            hotel_string = ', '.join(hotels_list)
        answers['hotels'] = hotel_string
        self.save_results(bot, answers)

    def save_results(self, bot: telebot, answers: Dict):
        """
        Сохраняет запрос пользователя в базу данных

        :param bot: объект бота
        :param answers: словарь, в который собирается информация от пользователя
        """
        update_query = '''INSERT INTO `user_requests` (`date_time`, `command`, `user_id`, `location`,
        `check_in_date`, `check_out_date`, `hotel_num`, `need_photo`, `photo_num`, `min_price`, `max_price`,
        `min_dist`, `max_dist`, `hotels_found`) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'''
        insert_data = (datetime.now(), self.command, self.user_id, answers.get('location'), answers.get('check-in'),
                       answers.get('check-out'), answers.get('hotel_num'), answers.get('need_photo'),
                       answers.get('photo_num', 0), answers.get('min_price'), answers.get('max_price'),
                       answers.get('min_dist'), answers.get('max_dist'), answers.get('hotels'))
        db_manage.update_line(update_query, insert_data)

        bot.send_message(self.chat, 'Если хочешь сделать новый запрос, выбери команду или введи /help',
                         reply_markup=keybords.help_keyboard())

    def stop_dialog(self, message, bot: telebot):
        """
        Проверяет, не запросил ли пользователь прервать выполнение команды

        :param message: объект сообщения
        :param bot: объект бота

        :return: True или None
        :rtype: bool or None
        """
        if message.text == 'Прервать поиск':
            bot.send_message(self.chat, 'Поиск прерван.')
            return True
