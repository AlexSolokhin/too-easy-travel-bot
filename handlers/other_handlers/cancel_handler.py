from loader import bot
from telebot.types import CallbackQuery
from utils.restart_and_cancel import cancel_search


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