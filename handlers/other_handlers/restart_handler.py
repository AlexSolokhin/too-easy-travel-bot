from loader import bot
from telebot.types import CallbackQuery
from utils.restart_and_cancel import restart_search


@bot.callback_query_handler(func=lambda call: call.data == 'TRY_AGAIN')
def restart_callback_handler(callback: CallbackQuery) -> None:
    """
    Вызов команды перезапуска поиска из коллбэка.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """
    bot.edit_message_reply_markup(callback.message.chat.id, callback.message.id, reply_markup=None)
    try_again_search(callback.from_user.id, callback.message.chat.id)
    bot.answer_callback_query(callback.id)
