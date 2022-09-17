from telebot import types


def hotel_details_keyboard(hotel_id: str,
                           hotel_link: str,
                           photo_shown: bool,
                           in_favorites: bool
                           ) -> types.InlineKeyboardMarkup:
    """
    Создаёт клавиатуру для действий с отелем.

    :param hotel_id: id отеля
    :type hotel_id: int
    :param hotel_link: ссылка на отель
    :type hotel_link: str
    :param photo_shown: флаг - показаны ли фото
    :type photo_shown: bool
    :param in_favorites: Флаг - добавлен ли в избранное
    :type in_favorites: bool
    :return: keyboard
    :rtype: InlineKeyboardMarkup
    """

    keyboard = types.InlineKeyboardMarkup()

    book = types.InlineKeyboardButton(text='Забронировать', url=hotel_link)
    show_photo = types.InlineKeyboardButton(text='Показать фото',
                                            callback_data='PHOTO|' + str(hotel_id))
    add_to_favorite = types.InlineKeyboardButton(text='Добавить в избранное',
                                                 callback_data='ADD_FAVORITE|' + str(hotel_id))
    delete_favorite = types.InlineKeyboardButton(text='Убрать из избранного',
                                                 callback_data='DELETE_FAVORITE|' + str(hotel_id))
    hide = types.InlineKeyboardButton(text='Скрыть', callback_data='HIDE')

    keyboard.add(book)
    if not photo_shown:
        keyboard.add(show_photo)
    if not in_favorites:
        keyboard.add(add_to_favorite)
    else:
        keyboard.add(delete_favorite)
    keyboard.add(hide)

    return keyboard
