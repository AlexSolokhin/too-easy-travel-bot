# TODO Функция History и Add_to_Favorite
# TODO Отредактировать docstring в единый формат
# TODO Настроить логирование
# TODO Сделать и использовать свои Exceptions

from loader import bot
import handlers
from telebot.custom_filters import StateFilter
from utils.set_bot_commands import set_default_commands

if __name__ == '__main__':
    bot.add_custom_filter(StateFilter(bot))
    set_default_commands(bot)
    bot.infinity_polling()
