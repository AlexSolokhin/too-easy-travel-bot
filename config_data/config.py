import os
from dotenv import load_dotenv, find_dotenv
from telebot_calendar import Calendar, CallbackData, RUSSIAN_LANGUAGE

if not find_dotenv():
    exit('Переменные окружения не загружены: проверьте файл .env')
else:
    load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Послать приветственное сообщение"),
    ('hello_world', "Ещё один способ послать приветственное сообщение"),
    ('lowprice', "Показывает топ самых дешевых отелей по выбранному направлению"),
    ('highprice', "Показывает топ самых дорогих отелей по выбранному направлению"),
    ('bestdeal', "Показывает топ предложений по запросу пользователя (близость к центру, цена)"),
    ('history', "Выдаёт историю поиска для пользователя"),
    ('help', "Выводит справку по командам бота")
)
CALENDAR = Calendar(RUSSIAN_LANGUAGE)
CALENDAR_CALLBACK = CallbackData("calendar", "action", "year", "month", "day")

