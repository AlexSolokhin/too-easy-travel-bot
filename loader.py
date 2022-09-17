from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
rapid_api = {"X-RapidAPI-Key": config.RAPID_API_KEY, "X-RapidAPI-Host": "hotels4.p.rapidapi.com"}