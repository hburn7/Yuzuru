from datetime import datetime
from peewee import CharField, DateTimeField, IntegerField, \
    BigIntegerField, TextField, ForeignKeyField, IdentityField, \
    BooleanField
from database import YuzuruModel


class User(YuzuruModel):
    id = IdentityField(unique=True)
    user_id = BigIntegerField()
    command_count = IntegerField(default=0)
    spirits = IntegerField(default=0)
    nsfw_age_confirm = BooleanField(default=False)
    nsfw_age_confirm_timestamp = DateTimeField(null=True)
    daily_last_claimed = DateTimeField(null=True)
    timestamp = DateTimeField(default=datetime.utcnow())


class CommandHistory(YuzuruModel):
    id = IdentityField()
    command = CharField()
    options = TextField(null=True)
    timestamp = DateTimeField(default=datetime.utcnow())
    user = ForeignKeyField(User, backref='commands')


class Log(YuzuruModel):
    id = IdentityField()
    guilds = IntegerField()
    users = IntegerField()
    commands = IntegerField()
    timestamp = DateTimeField(default=datetime.utcnow())
