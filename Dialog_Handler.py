import re

import db_manage
from Hotel_API import HotelAPIHandler
from keybords import simple_keyboard, yes_no_keyboard, one_to_ten_keybord
from datetime import datetime
from re import fullmatch


class Dialog:
    def __init__(self,  message, max_hotel=10, max_photo=10):
        self.command = message.text
        self.user_id = message.from_user.id
        self.chat = message.chat.id
        self.max_hotel = max_hotel
        self.max_photo = max_photo
        self.need_photo = 0

    def __call__(self, message, bot, *args, **kwargs):
        new_line_query = '''INSERT INTO user_requests (`date_time`, `command`, `user_id`) VALUES (?, ?, ?)'''
        insert_data = datetime.now(), self.command, self.user_id
        db_manage.update_line(new_line_query, insert_data)
        self.ask_location(message, bot, 'Куда ты хочешь отправиться?')

    def ask_location(self, message, bot, text):
        bot.send_message(self.chat, text, reply_markup=simple_keyboard())
        bot.register_next_step_handler(message, self.check_location, bot)

    def check_location(self, message, bot):
        location_update_query = '''UPDATE user_requests SET `location` = ? 
                WHERE id = (SELECT MAX(id) from user_requests) AND `user_id` = ?'''
        insert_data = (message.text, self.user_id)
        db_manage.update_line(location_update_query, insert_data)
        self.ask_dates(message, bot, 'Введи даты заезда и выезда в формате ДД-ММ-ГГ и раздели их одним пробелом.')

    def ask_dates(self, message, bot, text):
        bot.send_message(self.chat, text, reply_markup=simple_keyboard())
        bot.register_next_step_handler(message, self.check_dates, bot)

    def check_dates(self, message, bot):
        if not self.stop_dialog(message, bot):
            try:
                dates_list = message.text.split(' ')
                if len(dates_list) != 2:
                    raise IndexError('Введено слишком много пробелов')
                checkin_date = datetime.strptime(dates_list[0], '%d-%m-%y')
                checkout_date = datetime.strptime(dates_list[1], '%d-%m-%y')
                if checkout_date <= checkin_date or checkin_date < datetime.now() or checkout_date < datetime.now():
                    raise ValueError('Дата отъезда меньше даты заезда')
                dates_update_query = '''UPDATE user_requests SET `check_in_date` = ?, `check_out_date` = ? 
                                    WHERE id = (SELECT MAX(id) from user_requests) AND `user_id` = ?'''
                insert_data = (checkin_date, checkout_date, self.user_id)
                db_manage.update_line(dates_update_query, insert_data)
                self.ask_hotel_num(message, bot, 'Я могу показать до {} отелей. '
                                                 'Сколько отелей максимально тебе показать?'.format(self.max_hotel))
            except (ValueError, IndexError):
                self.ask_dates(message, bot, 'Неверный формат даты :(\n'
                                             'Убедись, что даты соответствуют формату "ДД-ММ-ГГ", '
                                             'что они разделены одним пробелом, и дата выезда позже даты заезда.\n'
                                             'Попробуй ещё раз или прерви поиск')

    def ask_hotel_num(self, message, bot, text):
        bot.send_message(self.chat, text, reply_markup=one_to_ten_keybord())
        bot.register_next_step_handler(message, self.check_hotel_num, bot)

    def check_hotel_num(self, message, bot):
        if not self.stop_dialog(message, bot):
            if not message.text.isdigit() or (self.max_hotel < int(message.text) or int(message.text) <= 0):
                self.ask_hotel_num(message, bot,
                                   'Пожалуйста, напиши, сколько максимально тебе показать отелей '
                                   'от 1 до {} или прерви поиск'
                                   .format(self.max_hotel))
            else:
                hotelnum_update_query = '''UPDATE user_requests SET `hotel_num` = ? 
                    WHERE id = (SELECT MAX(id) from user_requests) AND `user_id` = ?'''
                insert_data = (int(message.text), self.user_id)
                db_manage.update_line(hotelnum_update_query, insert_data)
                self.ask_need_photo(message, bot, 'Показать фото отеля?')

    def ask_need_photo(self, message, bot, text):
        bot.send_message(self.chat, text, reply_markup=yes_no_keyboard())
        bot.register_next_step_handler(message, self.check_need_photo, bot)

    def check_need_photo(self, message, bot):
        if not self.stop_dialog(message, bot):
            if message.text.lower() != 'да' and message.text.lower() != 'нет':
                self.ask_need_photo(message, bot, 'Пожалуйста, напиши нужны ли тебе фото (да или нет) '
                                                  'или прерви поиск!')
            else:
                needphoto_update_query = '''UPDATE user_requests SET `need_photo` = ? 
                WHERE id = (SELECT MAX(id) from user_requests) AND `user_id` = ?'''
                if message.text.lower() == 'да':
                    self.need_photo = 1
                insert_data = (self.need_photo, message.from_user.id)
                db_manage.update_line(needphoto_update_query, insert_data)
                if self.need_photo == 1:
                    self.ask_photo_num(message, bot, 'Я могу показать до {} фотографий. Сколько фото тебе показать?'
                                       .format(self.max_photo))
                elif self.command == '/bestdeal':
                    self.ask_price_limit(message, bot,
                                         'Укажи через "-" минимальную и максимальную цену за ночь в рублях, '
                                         'которая тебя бы устроила?')
                else:
                    self.proceed_result(bot, 'Спасибо! Начинаю обрабатывать твой запрос!')

    def ask_photo_num(self, message, bot, text):
        bot.send_message(self.chat, text, reply_markup=one_to_ten_keybord())
        bot.register_next_step_handler(message, self.check_photo_num, bot)

    def check_photo_num(self, message, bot):
        if not self.stop_dialog(message, bot):
            if not message.text.isdigit() or (self.max_photo < int(message.text) or int(message.text) < 0):
                self.ask_photo_num(message, bot,
                                   'Пожалуйста, напиши, сколько тебе показать фото от 1 до {} или прерви поиск'
                                   .format(self.max_photo))
            else:
                photonum_update_query = '''UPDATE user_requests SET `photo_num` = ? 
                                WHERE id = (SELECT MAX(id) from user_requests) AND `user_id` = ?'''
                insert_data = (int(message.text), self.user_id)
                db_manage.update_line(photonum_update_query, insert_data)
                if self.command == '/bestdeal':
                    self.ask_price_limit(message, bot, 'Укажи через "-" минимальную и максимальную '
                                                       'цену за ночь в рублях, которая тебя бы устроила?')
                else:
                    self.proceed_result(bot, 'Спасибо! Начинаю обрабатывать твой запрос!')

    def ask_price_limit(self, message, bot, text):
        bot.send_message(self.chat, text, reply_markup=simple_keyboard())
        bot.register_next_step_handler(message, self.check_price_limit, bot)

    def check_price_limit(self, message, bot):
        if not self.stop_dialog(message, bot):
            if not fullmatch(r'\d+\.?\d*\s?-\s?\d+\.?\d*', message.text) or \
                    float(''.join(message.text.split('-')[0].split())) > \
                    float(''.join(message.text.split('-')[1].split())):
                self.ask_price_limit(message, bot, 'Неверный формат сообщения :(\n'
                                                   'Пожалуйста, укажи через "-" минимальную и максимальную цену '
                                                   'за ночь в рублях?\n'
                                                   'Если нужно указать дробное значение, используй "."\n'
                                                   'Убедись, что первое значение меньше второго.')
            else:
                min_price = float(''.join(message.text.split('-')[0].split()))
                max_price = float(''.join(message.text.split('-')[1].split()))
                pricelimit_update_query = '''UPDATE user_requests SET `min_price` = ?, `max_price` = ? 
                WHERE id = (SELECT MAX(id) from user_requests) AND `user_id` = ?'''
                insert_data = (min_price, max_price, self.user_id)
                db_manage.update_line(pricelimit_update_query, insert_data)
                self.asc_dist_limit(message, bot,
                                    'Укажи через "-" '
                                    'минимальное и максимальное расстояние от центра в км, которое тебя бы устроило?')

    def asc_dist_limit(self, message, bot, text):
        bot.send_message(self.chat, text, reply_markup=simple_keyboard())
        bot.register_next_step_handler(message, self.check_dist_limit, bot)

    def check_dist_limit(self, message, bot):
        if not self.stop_dialog(message, bot):
            if not fullmatch(r'\d+\.?\d*\s?-\s?\d+\.?\d*', message.text) or \
                    float(''.join(message.text.split('-')[0].split())) > \
                    float(''.join(message.text.split('-')[1].split())):
                self.ask_price_limit(message, bot, 'Неверный формат сообщения :(\n'
                                                   'Пожалуйста, укажи минимальное и максимальное расстояние от центра, '
                                                   'которое тебя бы устроило?\n'
                                                   'Введи диапазон в км. через "-", дробные значения разделяй точкой.\n'
                                                   'Убедись, что первое значение меньше второго.')
            else:
                min_dist = float(''.join(message.text.split('-')[0].split()))
                max_dist = float(''.join(message.text.split('-')[1].split()))
                distlimit_update_query = '''UPDATE user_requests SET `min_dist` = ?, `max_dist` = ? 
                WHERE id = (SELECT MAX(id) from user_requests) AND `user_id` = ?'''
                insert_data = (min_dist, max_dist, self.user_id)
                db_manage.update_line(distlimit_update_query, insert_data)
                self.proceed_result(bot, 'Спасибо! Начинаю обрабатывать твой запрос!')

    def proceed_result(self, bot, text):
        bot.send_message(self.chat, text)
        last_line_query = '''SELECT `location`, `check_in_date`, `check_out_date`, `hotel_num`, 
        `photo_num`, `min_price`, `max_price`, `min_dist`, `max_dist` FROM user_requests
        WHERE id = (SELECT MAX(id) from user_requests) AND `user_id` = ?'''
        last_line = db_manage.get_line(last_line_query, (self.user_id, ))

        if self.command == '/highprice':
            sorting = 'PRICE_HIGHEST_FIRST'
        else:
            sorting = 'PRICE'

        check_in_date_obj = datetime.strptime(last_line[1], '%Y-%m-%d %H:%M:%S')
        check_out_date_obj = datetime.strptime(last_line[2], '%Y-%m-%d %H:%M:%S')

        searching_obj = HotelAPIHandler(check_in_date_obj, check_out_date_obj, last_line[3], self.need_photo,
                                        last_line[4], last_line[5], last_line[6], sorting, last_line[7], last_line[8])

        hotels_returned = searching_obj.find_hotels((searching_obj.find_location(last_line[0])))

        if isinstance(hotels_returned, str):
            bot.send_message(self.chat, hotels_returned)
            hotel_string = 'Отелей не найдено'
        else:
            full_days = (check_out_date_obj - check_in_date_obj).days

            hotels_list = []

            for hotels_num in range(0, max(len(hotels_returned), last_line[3])):
                price_per_night = float(re.sub(r'[^\d.]', '', hotels_returned[hotels_num]['price']))

                hotel_description = 'Отель: {hotel_name}\n' \
                                    'Расположен по адресу: {country},\t{city},\t{street_adr}\n' \
                                    'Расстояние от центра: {distance} км.\n' \
                                    'Цена за ночь: {price_per_night} рублей\n' \
                                    'Общая стоимость: {total_price} рублей\n'\
                    .format(hotel_name=hotels_returned[hotels_num]['name'],
                            country=hotels_returned[hotels_num]['address']['countryName'],
                            city=hotels_returned[hotels_num]['address']['locality'],
                            street_adr=hotels_returned[hotels_num]['address']
                            .get('streetAddress', 'Полный адрес доступен после бронирования.'),
                            distance=hotels_returned[hotels_num]['from_center'],
                            price_per_night=price_per_night,
                            total_price=price_per_night * full_days)

                hotels_list.append(hotels_returned[hotels_num]['name'])

                bot.send_message(self.chat, hotel_description)
                if hotels_returned[hotels_num].get('photo', None):
                    for photo_url in hotels_returned[hotels_num]['photo']:
                        bot.send_photo(self.chat, photo_url)

            hotel_string = ', '.join(hotels_list)

        hotels_found_update_query = '''UPDATE user_requests SET `hotels_found` = ? 
                WHERE id = (SELECT MAX(id) from user_requests) AND `user_id` = ?'''
        insert_data = (hotel_string, self.user_id)
        db_manage.update_line(hotels_found_update_query, insert_data)

    def stop_dialog(self, message, bot):
        if message.text == 'Прервать поиск':
            bot.send_message(self.chat, 'Поиск прерван.')
            return True
