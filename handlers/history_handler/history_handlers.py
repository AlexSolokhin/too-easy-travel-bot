from loader import bot
from config_data.config import db
from datetime import datetime
from telebot.types import Message, CallbackQuery
from states.travel_information import TravelInfoState
from database.db_models import History, Users
from database.history_db_methods import history_row_to_message
from keyboards.inline_keyboards.history import history_keyboard

# TODO Добавить условие, если история пуста

@bot.message_handler(commands=['history'])
def show_history(message: Message) -> None:
    """
    Показ истории поиска.

    :param message: Объект сообщения.
    :type message: Message
    :return: None
    """

    telegram_id = message.chat.id
    bot.set_state(message.from_user.id, TravelInfoState.show_history, message.chat.id)

    with db:
        user_history = History.select().join(Users).where(Users.telegram_id == telegram_id)
        for record in user_history:
            message_text = history_row_to_message(record)

            bot.send_message(message.chat.id, message_text,
                             reply_markup=history_keyboard(record.id),
                             parse_mode='MarkdownV2')


@bot.callback_query_handler(func=lambda call: call.data.startswith('DELETE'), state=TravelInfoState.show_history)
def delete_record(callback: CallbackQuery) -> None:
    """
    Удаление записи из истории.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """

    record_id = callback.data.split('|')[1]

    with db:
        record = History.select().where(History.id == record_id).get()
        record.delete_instance()

    bot.answer_callback_query(callback.id)
    bot.delete_message(callback.message.chat.id, callback.message.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('CLEAR'), state=TravelInfoState.show_history)
def delete_record(callback: CallbackQuery) -> None:
    """
    Очистка истории.

    :param callback: Объект CallBackQuery
    :type: CallbackQuery
    :return: None
    """

    telegram_id = callback.message.chat.id

    with db:
        user_history = History.select().join(Users).where(Users.telegram_id == telegram_id)
        for record in user_history:
            record.delete_instance()

    bot.answer_callback_query(callback.id)
    bot.send_message(telegram_id, 'История очищена')
