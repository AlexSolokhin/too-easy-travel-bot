from telebot.handler_backends import State, StatesGroup


class TravelInfoState(StatesGroup):
    location_type = State()
    location = State()
    specify_location = State()
    checkin_date = State()
    checkout_date = State()
    min_price = State()
    max_price = State()
    min_dist = State()
    max_dist = State()
    show_hotels = State()
    show_history = State()
    show_favorites = State()
