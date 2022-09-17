from datetime import datetime


def calendar_keyboard(calendar, calendar_callback):
    """
    Создаёт клавиатуру календаря.

    :return: keyboard
    :rtype: InlineKeyboardMarkup
    """

    keyboard = calendar.create_calendar(name=calendar_callback.prefix,
                                        year=datetime.now().year,
                                        month=datetime.now().month)
    return keyboard
