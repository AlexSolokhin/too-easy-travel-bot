import datetime
from config_data.config import db
from peewee import Model
from peewee import IntegerField, FloatField, CharField, ForeignKeyField, DateField, TimeField
from peewee import InternalError


class Users(Model):
    """
    Модель пользователя.
    """

    telegram_id = IntegerField(unique=True, null=False)

    class Meta:
        database = db
        db_table = 'users'


class History(Model):
    """
    Модель истории поиска.
    """

    user = ForeignKeyField(Users, on_delete='cascade')
    search_date = DateField(default=datetime.datetime.now().date())
    search_time = TimeField(default=datetime.datetime.now().time())
    command = CharField(max_length=10)
    location = CharField()
    checkin_date = CharField()
    checkout_date = CharField()
    min_price = IntegerField(null=True)
    max_price = IntegerField(null=True)
    min_dist = FloatField(null=True)
    max_dist = FloatField(null=True)
    hotels = CharField()

    class Meta:
        database = db
        db_table = 'history'


class Favorites(Model):
    """
    Модель для избранного.
    """

    user = ForeignKeyField(Users, on_delete='cascade')
    hotel_id = IntegerField()
    hotel = CharField(null=False)

    class Meta:
        database = db
        db_table = 'favorites'
